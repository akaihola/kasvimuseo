# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.models.autoconnect_photo_to_species``.

The receiver is connected to ``post_save`` for *every* model, not just for
``Photo``, so it runs on every ``save()`` the whole suite (and the whole
application) performs. That is why it has to stay cheap and total: it bails out
on a non-``Photo`` sender and on a title with no words, and it swallows
``Species.DoesNotExist``.
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
