from __future__ import unicode_literals

import pytest
from mock import patch

from kasvimuseo import photos


patch.object = patch.object


class MockPhoto(object):
    def __init__(self, pk, title):
        self.pk = pk
        self.title = '{} followed by other words'.format(title)

    def get_display_url(self):
        return '{}-{}.jpg'.format(self.title.split()[0], self.pk)


def test_get_photo_titles_pks_and_urls():
    with patch.object(photos.Photo, 'objects') as Photo_objects:
        Photo_objects.only().order_by.return_value = [MockPhoto(0, 'daffodil'),
                                                      MockPhoto(2, 'daffodil'),
                                                      MockPhoto(1, 'jonquil')]

        result = photos.get_photo_titles_pks_and_urls()

        assert result == [
            ('daffodil', {'pk': 0, 'url': 'daffodil-0.jpg'}),
            ('daffodil', {'pk': 2, 'url': 'daffodil-2.jpg'}),
            ('jonquil', {'pk': 1, 'url': 'jonquil-1.jpg'})]


def test_get_photo_pks_and_urls_by_species():
    with patch.object(photos, 'get_photo_titles_pks_and_urls') as g:
        g.return_value = [
            ('daffodil', {'pk': 0, 'url': 'daffodil-0.jpg'}),
            ('daffodil', {'pk': 2, 'url': 'daffodil-2.jpg'}),
            ('jonquil', {'pk': 1, 'url': 'jonquil-1.jpg'})]

        result = photos.get_photo_pks_and_urls_by_species()

        assert result == {
            'daffodil': [{'pk': 0, 'url': 'daffodil-0.jpg'},
                         {'pk': 2, 'url': 'daffodil-2.jpg'}],
            'jonquil': [{'pk': 1,
                         'url': 'jonquil-1.jpg'}]}


class MockSpecies(object):
    def __init__(self, name, photo):
        self.name_fi = name
        self.photo = photo


@pytest.mark.parametrize(
    'name, expect',
    [('daffodil', [(0, 'daffodil-0.jpg'),
                   (2, 'daffodil-2.jpg')]),
     ('jonquil', [(1, 'jonquil-1.jpg')]),
     ('foo', [])])
def test_get_species_photos(name, expect):
    species = MockSpecies(name, None)
    photo_pks_and_urls_by_title = {
        'daffodil': [{'pk': 0, 'url': 'daffodil-0.jpg'},
                     {'pk': 2, 'url': 'daffodil-2.jpg'}],
        'jonquil': [{'pk': 1, 'url': 'jonquil-1.jpg'}]}

    result = photos.get_species_photos(species, photo_pks_and_urls_by_title)

    assert result == expect


@pytest.mark.parametrize(
    'species, photo_pk, photo_title, expect',
    [('daffodil', None, None, (None, {0: 'daffodil-0.jpg',
                                      2: 'daffodil-2.jpg'})),
     ('daffodil', 0, 'daffodil photo', (0, {0: 'daffodil-0.jpg',
                                            2: 'daffodil-2.jpg'})),
     ('daffodil', 1, 'jonquil photo', (1, {0: 'daffodil-0.jpg',
                                           1: 'jonquil-1.jpg',
                                           2: 'daffodil-2.jpg'}))])
def test_get_species_photo_info(species, photo_pk, photo_title, expect):
    if photo_pk is None:
        photo = None
    else:
        photo = MockPhoto(photo_pk, photo_title)
    species = MockSpecies(species, photo)
    photo_pks_and_urls_by_title = {
        'daffodil': [{'pk': 0, 'url': 'daffodil-0.jpg'},
                     {'pk': 2, 'url': 'daffodil-2.jpg'}],
        'jonquil': [{'pk': 1, 'url': 'jonquil-1.jpg'}]}

    result = photos.get_species_photo_info(species,
                                           photo_pks_and_urls_by_title)


    assert result == expect


@pytest.mark.django_db
def test_get_candidate_photo_pks_matches_on_the_first_word(photo_factory):
    """The same key as the auto-attach receiver, case folded on both sides."""
    from kasvimuseo.tests.factories import create_species

    kukassa = photo_factory(title='Valkonarsissi kukassa')
    lehdet = photo_factory(title='valkonarsissi lehdet')
    photo_factory(title='keltanarsissi')

    pks = photos.get_candidate_photo_pks(create_species(name_fi='VALKONARSISSI'))

    assert sorted(pks) == sorted([kukassa.pk, lehdet.pk])


@pytest.mark.django_db
def test_get_candidate_photo_pks_of_a_nameless_species(photo_factory):
    from kasvimuseo.tests.factories import create_species

    photo_factory(title='valkonarsissi kukassa')

    assert photos.get_candidate_photo_pks(create_species(name_fi='')) == []
