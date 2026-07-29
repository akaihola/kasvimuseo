# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.photo_matching``.

The module decides which of several species sharing a Finnish name a photo
belongs to. It is tested here directly, without the ``post_save`` receiver in
the way, because the interesting cases are about what the garden records say
rather than about signals: the receiver's own behaviour is in
``test_signals.py``.

Every test that builds species builds *two* with the same ``name_fi``, since
that is the only situation this module is ever asked about.
"""

from __future__ import unicode_literals

import datetime

import pytest

from kasvimuseo import models, photo_matching
from kasvimuseo.tests.factories import (create_bed, create_care, create_label,
                                        create_location, create_observation,
                                        create_planting, create_species)

NAME = 'valkonarsissi'


def namesakes():
    """Two photoless species that cannot be told apart by name alone."""
    return (create_species(name_fi=NAME),
            create_species(name_fi=NAME, species='pseudonarcissus'))


def candidates():
    return models.Species.objects.filter(name_fi=NAME, photo__isnull=True)


def plant(species, removed=False, cares=(), origin=None, nickname=''):
    """Put ``species`` in the ground, optionally digging it up again."""
    observation = create_observation(species=species,
                                     origin=origin or create_location(),
                                     nickname=nickname)
    planting = create_planting(
        observation=observation,
        bed=create_bed(),
        removal_date=datetime.date(2021, 9, 1) if removed else None)
    for date in cares:
        create_care(planting, date=date)
    return planting


# -- normalisation and the file name ----------------------------------------

@pytest.mark.parametrize('text,expected', [
    ('Valkonarsissi', ['valkonarsissi']),
    ('Sääksmäen Yrttitarha', ['saaksmaen', 'yrttitarha']),
    ('iso-mattila_2019', ['iso', 'mattila', '2019']),
    ('', []),
    (None, []),
])
def test_normalize_folds_case_accents_and_separators(text, expected):
    assert photo_matching.normalize(text) == expected


def test_normalize_accepts_bytes():
    assert photo_matching.normalize('Yläne'.encode('utf-8')) == ['ylane']


def test_filename_targets_drops_the_path_and_the_extension():
    targets = photo_matching.filename_targets('photologue/photos/ylane.jpg')

    assert targets == {'ylane'}


def test_filename_targets_joins_runs_of_words():
    targets = photo_matching.filename_targets('narsissi-iso-mattila.jpg')

    # Each word on its own, and the runs, so a two-word place name matches.
    assert 'isomattila' in targets
    assert 'narsissi' in targets
    assert 'narsissiisomattila' in targets


def test_best_ratio_is_one_for_a_name_written_into_the_file_name():
    targets = photo_matching.filename_targets('valkonarsissi-kukassa.jpg')

    assert photo_matching.best_ratio('Valkonarsissi', targets) == 1.0


def test_best_ratio_is_low_for_an_unrelated_name():
    targets = photo_matching.filename_targets('syyshortensia.jpg')

    assert photo_matching.best_ratio('Valkonarsissi', targets) < 0.5


def test_best_ratio_of_a_value_with_nothing_to_compare_is_zero():
    assert photo_matching.best_ratio('', {'valkonarsissi'}) == 0.0
    assert photo_matching.best_ratio('valkonarsissi', set()) == 0.0


# -- scoring -----------------------------------------------------------------

@pytest.mark.django_db
def test_similarity_score_adds_up_the_fields_that_match():
    """Two fields naming the same species beat one, which is the whole point.

    Both candidates are called ``valkonarsissi``; only one of them came from
    Mattila, and the file name says Mattila.
    """
    first, second = namesakes()
    plant(first, origin=create_location(name='Mattila'))
    plant(second, origin=create_location(name='Koivula'))
    targets = photo_matching.filename_targets('valkonarsissi-mattila.jpg')

    assert (photo_matching.similarity_score(first, targets) >
            photo_matching.similarity_score(second, targets))


@pytest.mark.django_db
def test_similarity_score_ignores_fields_that_merely_resemble():
    """Below the threshold a field contributes nothing at all."""
    species = create_species(name_fi=NAME, genus='Narcissus')
    targets = photo_matching.filename_targets('syyshortensia.jpg')

    assert photo_matching.similarity_score(species, targets) == 0.0


# -- the cascade -------------------------------------------------------------

@pytest.mark.django_db
def test_the_observed_species_wins():
    first, second = namesakes()
    create_observation(species=first)

    assert photo_matching.disambiguate(candidates(), 'kuva.jpg') == first


@pytest.mark.django_db
def test_a_criterion_that_would_leave_nothing_is_skipped():
    """Absent evidence is not evidence against either candidate.

    Neither species has ever been observed, so the observation filter is
    skipped rather than applied -- and because nothing further separates them,
    the answer is still that there is no answer.
    """
    namesakes()

    assert photo_matching.disambiguate(candidates(), 'kuva.jpg') is None


@pytest.mark.django_db
def test_the_species_still_in_the_ground_wins():
    first, second = namesakes()
    plant(first, removed=True)
    plant(second)

    assert photo_matching.disambiguate(candidates(), 'kuva.jpg') == second


@pytest.mark.django_db
def test_the_labelled_species_wins():
    first, second = namesakes()
    plant(first)
    plant(second)
    create_label(species=second)

    assert photo_matching.disambiguate(candidates(), 'kuva.jpg') == second


@pytest.mark.django_db
def test_the_most_recently_cared_for_species_wins():
    first, second = namesakes()
    plant(first, cares=[datetime.date(2020, 6, 1)])
    plant(second, cares=[datetime.date(2022, 6, 1)])

    assert photo_matching.disambiguate(candidates(), 'kuva.jpg') == second


@pytest.mark.django_db
def test_care_of_a_planting_that_has_been_removed_does_not_count():
    """The removal date and the aggregate have to share one join.

    ``first`` was cared for more recently than ``second``, but on a planting
    that has since been dug up. If the two conditions end up in separate joins
    the query answers with that date anyway and the wrong species wins.
    """
    first, second = namesakes()
    plant(first, cares=[datetime.date(2020, 6, 1)])
    plant(first, removed=True, cares=[datetime.date(2024, 6, 1)])
    plant(second, cares=[datetime.date(2022, 6, 1)])

    assert photo_matching.disambiguate(candidates(), 'kuva.jpg') == second


@pytest.mark.django_db
def test_the_file_name_decides_what_the_garden_records_cannot():
    """Same evidence on both sides; the file name names one of the houses."""
    first, second = namesakes()
    plant(first, origin=create_location(name='Mattila'))
    plant(second, origin=create_location(name='Koivula'))

    assert photo_matching.disambiguate(
        candidates(), 'valkonarsissi-mattila-2019.jpg') == first


@pytest.mark.django_db
def test_the_file_name_can_name_a_nickname_instead():
    first, second = namesakes()
    plant(first, nickname='Mummon narsissi')
    plant(second)

    assert photo_matching.disambiguate(
        candidates(), 'mummon-narsissi.jpg') == first


@pytest.mark.django_db
def test_two_species_with_the_same_story_are_left_alone():
    """The point of the whole exercise: no winner means no photo attached."""
    origin = create_location(name='Mattila')
    first, second = namesakes()
    plant(first, origin=origin, cares=[datetime.date(2022, 6, 1)])
    plant(second, origin=origin, cares=[datetime.date(2022, 6, 1)])

    assert photo_matching.disambiguate(
        candidates(), 'valkonarsissi-mattila.jpg') is None


@pytest.mark.django_db
def test_a_file_name_naming_neither_species_decides_nothing():
    first, second = namesakes()
    plant(first, origin=create_location(name='Mattila'))
    plant(second, origin=create_location(name='Koivula'))

    assert photo_matching.disambiguate(candidates(), 'IMG_4021.jpg') is None
