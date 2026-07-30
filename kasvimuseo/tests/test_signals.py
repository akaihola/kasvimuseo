# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.models.autoconnect_photo_to_species``.

The receiver is connected to ``post_save`` for ``Photo``, and it keeps its own
``sender != Photo`` guard, so calling it for any other model is a no-op. It has
to stay cheap and total, because it runs on every ``Photo`` the application
saves: it bails out on a title with no words, and it never raises on a lookup
that fails or matches too much. ``name_fi`` carries no unique constraint, so a
title can name several species; those go to ``kasvimuseo.photo_matching``,
which is tested on its own in ``test_photo_matching.py``. What is tested here
is that the receiver asks it and abides by the answer, including the answer
"no".
"""

from __future__ import unicode_literals

import datetime

import pytest

from kasvimuseo import models
from kasvimuseo.tests.factories import (create_bed, create_care,
                                        create_location, create_observation,
                                        create_planting, create_species)


@pytest.mark.django_db
def test_photo_attaches_itself_to_matching_species(photo_factory):
    species = create_species(name_fi='valkonarsissi')

    photo = photo_factory(title='Valkonarsissi kukassa')

    species = models.Species.objects.get(pk=species.pk)
    assert species.photo == photo


@pytest.mark.django_db
def test_photo_replaces_an_existing_species_photo(photo_factory):
    """Deliberately the opposite of what this test used to assert.

    Until issue 042 the lookup carried ``photo__isnull=True``, so the first
    photo uploaded for a species won permanently and every later one was
    ignored -- and since this receiver is the only place ``Species.photo`` is
    ever set, that made the picture unchangeable without a Django shell. The
    photo saved last now wins.
    """
    species = create_species(name_fi='valkonarsissi')
    first = photo_factory(title='valkonarsissi kukassa')
    assert models.Species.objects.get(pk=species.pk).photo == first

    second = photo_factory(title='valkonarsissi lehdet')

    assert models.Species.objects.get(pk=species.pk).photo == second


@pytest.mark.django_db
def test_a_better_photo_uploaded_later_replaces_the_first_one(photo_factory):
    """The case as it was reported, with the names it was reported under.

    ``Sammalleimu`` had the photograph taken at Airila; a new one taken at
    Tottila was uploaded and titled after the species, and the species list
    went on showing the Airila one. Nothing was ambiguous -- the species simply
    already had a photo, so the lookup matched nothing at all.
    """
    species = create_species(name_fi='sammalleimu', genus='Lysimachia')
    airila = photo_factory(title='Sammalleimu Airila 19',
                           filename='Sammalleimu. Airila.19')
    assert models.Species.objects.get(pk=species.pk).photo == airila

    tottila = photo_factory(title='Sammalleimu Tottila 19',
                            filename='Sammalleimu Tottila 19')

    assert models.Species.objects.get(pk=species.pk).photo == tottila


@pytest.mark.django_db
def test_a_replacement_goes_to_the_right_one_of_two_namesakes(photo_factory):
    """The one duplicate ``name_fi`` the production data actually has.

    Two ``tarhakurjenmiekka``, and both already have a photo -- so once issue
    042 stopped ``photo__isnull=True`` narrowing the candidates, every photo
    titled after them is ambiguous and 002's disambiguation has to earn its
    keep. Both of their existing photographs are named after the house they
    were taken at, which is what tells them apart.
    """
    kurala = create_species(name_fi='tarhakurjenmiekka', genus='Iris')
    peltomaki = create_species(name_fi='tarhakurjenmiekka', genus='Iris',
                               species="'Cracchus'")
    for species, house in ((kurala, 'Kurala'), (peltomaki, 'Peltomäki')):
        create_observation(species=species,
                           origin=create_location(name=house))
        species.photo = photo_factory(title='vanha kuva {0}'.format(house),
                                      filename='vanha-{0}'.format(house))
        species.save()

    photo = photo_factory(title='Tarhakurjenmiekka Kurala 02',
                          filename='Tarhakurjenmiekka.Kurala.183')

    assert models.Species.objects.get(pk=kurala.pk).photo == photo
    assert models.Species.objects.get(pk=peltomaki.pk).photo != photo


@pytest.mark.django_db
def test_photo_attaches_to_a_species_whose_name_is_capitalised(photo_factory):
    """The direction that could not work before issue 003.

    The title word was lower-cased and then compared to ``name_fi`` exactly, so
    a species entered with a capital initial -- which the admin does nothing to
    prevent -- was unreachable however the photo was titled.
    """
    species = create_species(name_fi='Valkonarsissi')

    photo = photo_factory(title='valkonarsissi kukassa')

    assert models.Species.objects.get(pk=species.pk).photo == photo


@pytest.mark.django_db
def test_photo_attaches_when_neither_case_matches_the_other(photo_factory):
    """Case decides nothing on either side, not just on the title's."""
    species = create_species(name_fi='Valkonarsissi')

    photo = photo_factory(title='VALKONARSISSI kukassa')

    assert models.Species.objects.get(pk=species.pk).photo == photo


@pytest.mark.django_db
def test_a_species_with_a_blank_name_matches_nothing(photo_factory):
    """A blank ``name_fi`` is "no name", not a name that matches everything."""
    nameless = create_species(name_fi='')

    photo_factory(title='valkonarsissi kukassa')

    assert models.Species.objects.get(pk=nameless.pk).photo is None


@pytest.mark.django_db
def test_photo_with_no_matching_species_leaves_every_species_alone(
        photo_factory):
    create_species(name_fi='valkonarsissi')
    create_species(name_fi='tulppaani', genus='Tulipa')

    photo_factory(title='syyshortensia kukassa')

    assert not models.Species.objects.filter(photo__isnull=False).exists()


@pytest.mark.django_db
def test_photo_with_an_empty_title_returns_early(photo_factory):
    create_species(name_fi='valkonarsissi')

    photo_factory(title='')

    assert not models.Species.objects.filter(photo__isnull=False).exists()


@pytest.mark.django_db
def test_saving_a_non_photo_model_does_not_attach_anything(photo_factory):
    photo_factory(title='valkonarsissi kukassa')

    # Saving a Species also fires post_save, with sender=Species.
    species = create_species(name_fi='valkonarsissi')

    assert models.Species.objects.get(pk=species.pk).photo is None


@pytest.mark.django_db
def test_the_receiver_is_a_no_op_when_called_for_another_sender():
    """The guard, not just the ``sender=Photo`` connection, is what protects.

    The receiver is connected for ``Photo`` alone, so no other model reaches it
    through ``post_save`` any more. Call it directly to pin the guard itself,
    which is what makes that narrowing behaviour-preserving.
    """
    species = create_species(name_fi='valkonarsissi')

    assert models.autoconnect_photo_to_species(
        sender=models.Species, instance=species) is None
    assert models.Species.objects.get(pk=species.pk).photo is None


@pytest.mark.django_db
def test_photo_matching_two_indistinguishable_species_attaches_to_neither(
        photo_factory):
    """``name_fi`` is not unique, so the lookup can match more than once.

    Before this was fixed the ambiguous lookup raised
    ``MultipleObjectsReturned`` out of ``post_save``, which failed the whole
    ``Photo`` save -- in the admin as well. Nothing in the garden records or in
    the file name tells these two apart, so the save completes and the photo is
    attached to neither: picking one would be a guess.
    """
    first = create_species(name_fi='valkonarsissi')
    second = create_species(name_fi='valkonarsissi', species='pseudonarcissus')

    photo = photo_factory(title='Valkonarsissi kukassa')

    assert models.Photo.objects.filter(pk=photo.pk).exists()
    assert models.Species.objects.get(pk=first.pk).photo is None
    assert models.Species.objects.get(pk=second.pk).photo is None


@pytest.mark.django_db
def test_photo_goes_to_the_namesake_that_is_actually_in_the_garden(
        photo_factory):
    """Ambiguous by name, settled by the records: one of the two is planted."""
    first = create_species(name_fi='valkonarsissi')
    second = create_species(name_fi='valkonarsissi', species='pseudonarcissus')
    create_planting(observation=create_observation(species=second),
                    bed=create_bed())

    photo = photo_factory(title='Valkonarsissi kukassa')

    assert models.Species.objects.get(pk=second.pk).photo == photo
    assert models.Species.objects.get(pk=first.pk).photo is None


@pytest.mark.django_db
def test_the_file_name_settles_what_the_title_cannot(photo_factory):
    """The title chooses the species; the file name tells namesakes apart.

    Both are planted and both were cared for on the same day, so the records
    are no help. The photograph is named after the house one of them came
    from, which is how these files tend to be named.
    """
    first = create_species(name_fi='valkonarsissi')
    second = create_species(name_fi='valkonarsissi', species='pseudonarcissus')
    for species, house in ((first, 'Mattila'), (second, 'Koivula')):
        planting = create_planting(
            observation=create_observation(
                species=species, origin=create_location(name=house)),
            bed=create_bed())
        create_care(planting, date=datetime.date(2022, 6, 1))

    photo = photo_factory(title='Valkonarsissi kukassa',
                          filename='valkonarsissi-mattila-2019')

    assert models.Species.objects.get(pk=first.pk).photo == photo
    assert models.Species.objects.get(pk=second.pk).photo is None


@pytest.mark.django_db
def test_photo_attaches_when_only_one_of_two_namesakes_lacks_a_photo(
        photo_factory):
    """One photoless match is still one match, however many namesakes exist."""
    taken = create_species(name_fi='valkonarsissi')
    taken.photo = photo_factory(title='valkonarsissi lehdet')
    taken.save()
    free = create_species(name_fi='valkonarsissi', species='pseudonarcissus')

    photo = photo_factory(title='valkonarsissi kukassa')

    assert models.Species.objects.get(pk=free.pk).photo == photo
