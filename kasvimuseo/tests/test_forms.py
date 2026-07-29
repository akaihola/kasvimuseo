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


@pytest.mark.django_db
def test_clean_leaves_uniqueness_checking_switched_on():
    """``BaseModelForm.clean()`` is the only thing that sets this flag.

    An override that forgets to call it switches off ``validate_unique()`` for
    the whole form, which is not a validation nicety here: ``Photo.title`` and
    ``Photo.title_slug`` are unique, so the check is all that stands between a
    duplicate title and an ``IntegrityError`` from PostgreSQL.
    """
    form = PhotoForm()
    form.cleaned_data = {'image': FakeImage('valkonarsissi.jpg'),
                         'title': '',
                         'title_slug': ''}

    form.clean()

    assert form._validate_unique is True


@pytest.mark.django_db
def test_clean_survives_a_missing_image():
    """``image`` is the one required field, so it can be absent from a POST.

    ``clean()`` runs after field validation either way, so it has to cope with
    a ``cleaned_data`` that has no image in it rather than raising ``KeyError``
    and turning a form error into a 500.
    """
    form = PhotoForm()
    form.cleaned_data = {'title': '', 'title_slug': ''}

    cleaned = form.clean()

    assert cleaned['title'] == ''
    assert cleaned['title_slug'] == ''


@pytest.mark.django_db
def test_a_duplicate_title_is_a_form_error_not_a_database_error(photo_factory,
                                                               media_root):
    """Uploading a second photo under a title already in use.

    This is what "upload a better photo of the same plant" looks like when the
    photographer names both files the same way. It has to come back as an error
    on the form: without ``validate_unique`` the insert reaches the database,
    and by then the uploaded file has been written, leaving an image on disk
    that no row points at.
    """
    from django.core.files.uploadedfile import SimpleUploadedFile
    from kasvimuseo.tests.conftest import jpeg_bytes
    photo_factory(title='valkonarsissi kukassa')

    form = PhotoForm(
        data={'title': 'valkonarsissi kukassa',
              'title_slug': '',
              'caption': '',
              'crop_from': 'center',
              'date_added': '2026-07-29 12:00:00',
              'tags': ''},
        files={'image': SimpleUploadedFile('toinen.jpg', jpeg_bytes(),
                                           content_type=str('image/jpeg'))})

    assert not form.is_valid()
    # Both unique fields are reported: the slug is derived from the title, so a
    # duplicate title brings a duplicate slug with it.
    assert sorted(form.errors) == ['title', 'title_slug'], form.errors


def test_remove_diacritics_returns_a_text_string():
    """Pin the Python 2 behaviour of ``filter()`` over a unicode string.

    On Python 3 ``filter()`` returns an iterator, so ``slugify`` would receive
    a ``<filter object ...>`` repr and silently mangle every slug. This test
    fails loudly at migration time instead. See docs/issues/016.
    """
    result = remove_diacritics('Kevätesikko ähkyssä')
    assert isinstance(result, type('')), \
        'remove_diacritics returned {0!r}, not a text string'.format(result)
    assert result == 'Kevatesikko ahkyssa'
