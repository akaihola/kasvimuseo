# -*- coding: utf-8 -*-
"""Database-backed counterpart to the mock-based ``test_photos``.

``test_photos`` replaces ``photologue.models.Photo`` wholesale, so it cannot
notice a photologue API change. These tests run the same four functions against
real rows and a real ``get_display_url()``.
"""

from __future__ import unicode_literals

import pytest

from kasvimuseo import photos
from kasvimuseo.tests.factories import create_species


@pytest.fixture
def display_size(db):
    """The ``display`` photo size ``get_display_url()`` is named after.

    Photologue ships one in its initial data, but the accessor methods are
    attached at ``post_init`` from ``PhotoSizeCache``, a Borg whose state
    outlives the test transaction. Reset it on both sides: before, so the size
    is loaded, and after, so nothing rolled back leaks into later tests.
    """
    from photologue.models import PhotoSize, PhotoSizeCache

    PhotoSizeCache().reset()
    PhotoSize.objects.get_or_create(name='display',
                                    defaults={'width': 100, 'height': 100})
    yield
    PhotoSizeCache().reset()


@pytest.mark.django_db
def test_get_photo_titles_pks_and_urls(display_size, photo_factory):
    second = photo_factory(title='valkonarsissi kukassa')
    first = photo_factory(title='tulppaani kukassa')

    result = photos.get_photo_titles_pks_and_urls()

    assert [title for title, _ in result] == ['tulppaani', 'valkonarsissi']
    assert [info['pk'] for _, info in result] == [first.pk, second.pk]
    assert [info['url'] for _, info in result] == [first.get_display_url(),
                                                   second.get_display_url()]
    # The url is photologue's cached "display" rendition, not the original.
    assert '/photologue/photos/cache/' in result[0][1]['url']
    assert result[0][1]['url'].endswith('_display.jpg')


@pytest.mark.django_db
def test_get_photo_pks_and_urls_by_species(display_size, photo_factory):
    kukassa = photo_factory(title='valkonarsissi kukassa')
    lehdet = photo_factory(title='valkonarsissi lehdet')
    tulppaani = photo_factory(title='tulppaani kukassa')

    result = photos.get_photo_pks_and_urls_by_species()

    assert sorted(result.keys()) == ['tulppaani', 'valkonarsissi']
    assert [info['pk'] for info in result['valkonarsissi']] == [kukassa.pk,
                                                                lehdet.pk]
    assert [info['pk'] for info in result['tulppaani']] == [tulppaani.pk]


@pytest.mark.django_db
def test_get_species_photos(display_size, photo_factory):
    kukassa = photo_factory(title='valkonarsissi kukassa')
    lehdet = photo_factory(title='valkonarsissi lehdet')
    photo_factory(title='tulppaani kukassa')
    by_species = photos.get_photo_pks_and_urls_by_species()
    # Created after the photos, so the post_save receiver cannot have attached
    # one of them to either species.
    valkonarsissi = create_species(name_fi='valkonarsissi')
    syyshortensia = create_species(name_fi='syyshortensia', genus='Hydrangea')

    assert photos.get_species_photos(valkonarsissi, by_species) == [
        (kukassa.pk, kukassa.get_display_url()),
        (lehdet.pk, lehdet.get_display_url())]
    assert photos.get_species_photos(syyshortensia, by_species) == []


@pytest.mark.django_db
def test_get_species_photos_ignores_case(display_size, photo_factory):
    """Issue 003: neither the title's case nor ``name_fi``'s decides a match.

    Also that the two photos land in *one* group: their keys are equal only
    after case-folding, and in title order they are not adjacent.
    """
    kukassa = photo_factory(title='Valkonarsissi kukassa')
    lehdet = photo_factory(title='valkonarsissi lehdet')
    by_species = photos.get_photo_pks_and_urls_by_species()
    capitalised = create_species(name_fi='Valkonarsissi')
    lower_case = create_species(name_fi='valkonarsissi',
                                species='pseudonarcissus')

    expected = [(kukassa.pk, kukassa.get_display_url()),
                (lehdet.pk, lehdet.get_display_url())]
    assert photos.get_species_photos(capitalised, by_species) == expected
    assert photos.get_species_photos(lower_case, by_species) == expected


@pytest.mark.django_db
def test_get_species_photos_of_a_species_with_a_blank_name(display_size,
                                                           photo_factory):
    """``name_fi.split()[0]`` used to raise ``IndexError`` here."""
    photo_factory(title='valkonarsissi kukassa')
    by_species = photos.get_photo_pks_and_urls_by_species()
    nameless = create_species(name_fi='')

    assert photos.get_species_photos(nameless, by_species) == []


@pytest.mark.django_db
def test_get_photo_titles_pks_and_urls_skips_an_untitled_photo(display_size,
                                                               photo_factory):
    """A photo with no word in its title names nothing, and does not raise."""
    photo_factory(title='valkonarsissi kukassa')
    photo_factory(title='', filename='untitled')

    result = photos.get_photo_titles_pks_and_urls()

    assert [title for title, _ in result] == ['valkonarsissi']


@pytest.mark.django_db
def test_get_species_photo_info_with_a_photo_set(display_size, photo_factory):
    kukassa = photo_factory(title='valkonarsissi kukassa')
    tulppaani = photo_factory(title='tulppaani kukassa')
    by_species = photos.get_photo_pks_and_urls_by_species()
    species = create_species(name_fi='valkonarsissi', photo=tulppaani)

    photo_pk, urls = photos.get_species_photo_info(species, by_species)

    assert photo_pk == tulppaani.pk
    # The selected photo is offered alongside the ones matched by title.
    assert urls == {kukassa.pk: kukassa.get_display_url(),
                    tulppaani.pk: tulppaani.get_display_url()}


@pytest.mark.django_db
def test_get_species_photo_info_without_a_photo_set(display_size,
                                                    photo_factory):
    kukassa = photo_factory(title='valkonarsissi kukassa')
    by_species = photos.get_photo_pks_and_urls_by_species()
    species = create_species(name_fi='valkonarsissi')

    photo_pk, urls = photos.get_species_photo_info(species, by_species)

    assert photo_pk is None
    assert urls == {kukassa.pk: kukassa.get_display_url()}
