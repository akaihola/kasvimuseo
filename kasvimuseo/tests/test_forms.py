# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.forms``."""

from __future__ import unicode_literals

import pytest

from kasvimuseo.forms import PhotoForm, remove_diacritics


class FakeImage(object):
    def __init__(self, name):
        self.name = name


def clean(image_name, title='', title_slug=''):
    """Run ``PhotoForm.clean`` over a hand-built ``cleaned_data``.

    Constructing the form instantiates a photologue ``Photo``, whose
    ``post_init`` receiver reads the ``PhotoSize`` table -- hence the
    ``django_db`` mark on every test that calls this.
    """
    form = PhotoForm()
    form.cleaned_data = {'image': FakeImage(image_name),
                         'title': title,
                         'title_slug': title_slug}
    return form.clean()


@pytest.mark.django_db
@pytest.mark.parametrize('image_name,expected_title', [
    ('valkonarsissi.jpg', 'valkonarsissi'),
    ('valkonarsissi.jpeg', 'valkonarsissi'),
    ('valkonarsissi.jpe', 'valkonarsissi'),
    ('valkonarsissi.JPG', 'valkonarsissi'),
    ('valkonarsissi.JPEG', 'valkonarsissi'),
    ('valkonarsissi.JPE', 'valkonarsissi'),
    # Only the extension is dropped; other dots become spaces.
    ('kevät 2020.valkonarsissi.jpg', 'kevät 2020 valkonarsissi'),
    # An unrecognised extension is kept, as a space-separated word.
    ('valkonarsissi.png', 'valkonarsissi png'),
])
def test_clean_derives_the_title_from_the_file_name(image_name,
                                                    expected_title):
    assert clean(image_name)['title'] == expected_title


@pytest.mark.django_db
def test_clean_keeps_a_supplied_title():
    cleaned = clean('valkonarsissi.jpg', title='Mummon narsissi')
    assert cleaned['title'] == 'Mummon narsissi'
    assert cleaned['title_slug'] == 'mummon-narsissi'


@pytest.mark.django_db
def test_clean_treats_a_blank_title_as_missing():
    assert clean('valkonarsissi.jpg', title='   ')['title'] == 'valkonarsissi'


@pytest.mark.django_db
def test_clean_slugifies_the_title_without_diacritics():
    assert clean('Kevätesikko ähkyssä.jpg')['title_slug'] == \
        'kevatesikko-ahkyssa'


@pytest.mark.django_db
def test_clean_keeps_a_supplied_slug():
    cleaned = clean('valkonarsissi.jpg', title_slug='oma-slug')
    assert cleaned['title_slug'] == 'oma-slug'


def test_remove_diacritics_returns_a_text_string():
    """Pin the Python 2 behaviour of ``filter()`` over a unicode string.

    On Python 3 ``filter()`` returns an iterator, so ``slugify`` would receive
    a ``<filter object ...>`` repr and silently mangle every slug. This test
    fails loudly at migration time instead.
    """
    result = remove_diacritics('Kevätesikko ähkyssä')
    assert isinstance(result, type('')), \
        'remove_diacritics returned {0!r}, not a text string'.format(result)
    assert result == 'Kevatesikko ahkyssa'
