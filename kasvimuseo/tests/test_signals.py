# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.models.autoconnect_photo_to_species``.

The receiver is connected to ``post_save`` for ``Photo``, and it keeps its own
``sender != Photo`` guard, so calling it for any other model is a no-op. It has
to stay cheap and total, because it runs on every ``Photo`` the application
saves: it bails out on a title with no words, and it swallows both
``Species.DoesNotExist`` and ``Species.MultipleObjectsReturned`` -- ``name_fi``
carries no unique constraint, so an ambiguous match is possible on the
production data.
"""

from __future__ import unicode_literals

import pytest

from kasvimuseo import models
from kasvimuseo.tests.factories import create_species


@pytest.mark.django_db
def test_photo_attaches_itself_to_matching_species(photo_factory):
    species = create_species(name_fi='valkonarsissi')

    photo = photo_factory(title='Valkonarsissi kukassa')

    species = models.Species.objects.get(pk=species.pk)
    assert species.photo == photo


@pytest.mark.django_db
def test_photo_does_not_overwrite_an_existing_species_photo(photo_factory):
    species = create_species(name_fi='valkonarsissi')
    first = photo_factory(title='valkonarsissi kukassa')
    assert models.Species.objects.get(pk=species.pk).photo == first

    photo_factory(title='valkonarsissi lehdet')

    assert models.Species.objects.get(pk=species.pk).photo == first


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
def test_photo_matching_two_photoless_species_attaches_to_neither(
        photo_factory):
    """``name_fi`` is not unique, so the lookup can match more than once.

    Before this was fixed the ambiguous lookup raised
    ``MultipleObjectsReturned`` out of ``post_save``, which failed the whole
    ``Photo`` save -- in the admin as well. The save now completes and the
    photo is attached to neither candidate, because picking one of them would
    be a guess.
    """
    first = create_species(name_fi='valkonarsissi')
    second = create_species(name_fi='valkonarsissi', species='pseudonarcissus')

    photo = photo_factory(title='Valkonarsissi kukassa')

    assert models.Photo.objects.filter(pk=photo.pk).exists()
    assert models.Species.objects.get(pk=first.pk).photo is None
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
