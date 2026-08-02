# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.forms``."""

from __future__ import unicode_literals

import pytest

from kasvimuseo.forms import PhotoForm, SpeciesForm, remove_diacritics
from kasvimuseo.tests.factories import create_species


class FakeImage(object):
    def __init__(self, name):
        self.name = name


def clean(image_name, title='', slug=''):
    """Run ``PhotoForm.clean`` over a hand-built ``cleaned_data``.

    Constructing the form instantiates a photologue ``Photo``, whose
    ``post_init`` receiver reads the ``PhotoSize`` table -- hence the
    ``django_db`` mark on every test that calls this.
    """
    form = PhotoForm()
    form.cleaned_data = {'image': FakeImage(image_name),
                         'title': title,
                         'slug': slug}
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
    assert cleaned['slug'] == 'mummon-narsissi'


@pytest.mark.django_db
def test_clean_treats_a_blank_title_as_missing():
    assert clean('valkonarsissi.jpg', title='   ')['title'] == 'valkonarsissi'


@pytest.mark.django_db
def test_clean_slugifies_the_title_without_diacritics():
    assert clean('Kevätesikko ähkyssä.jpg')['slug'] == \
        'kevatesikko-ahkyssa'


@pytest.mark.django_db
def test_clean_keeps_a_supplied_slug():
    cleaned = clean('valkonarsissi.jpg', slug='oma-slug')
    assert cleaned['slug'] == 'oma-slug'


@pytest.mark.django_db
def test_clean_leaves_uniqueness_checking_switched_on():
    """``BaseModelForm.clean()`` is the only thing that sets this flag.

    An override that forgets to call it switches off ``validate_unique()`` for
    the whole form, which is not a validation nicety here: ``Photo.title`` and
    ``Photo.slug`` are unique, so the check is all that stands between a
    duplicate title and an ``IntegrityError`` from PostgreSQL.
    """
    form = PhotoForm()
    form.cleaned_data = {'image': FakeImage('valkonarsissi.jpg'),
                         'title': '',
                         'slug': ''}

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
    form.cleaned_data = {'title': '', 'slug': ''}

    cleaned = form.clean()

    assert cleaned['title'] == ''
    assert cleaned['slug'] == ''


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
              'slug': '',
              'caption': '',
              'crop_from': 'center',
              'date_added': '2026-07-29 12:00:00',
              'tags': ''},
        files={'image': SimpleUploadedFile('toinen.jpg', jpeg_bytes(),
                                           content_type=str('image/jpeg'))})

    assert not form.is_valid()
    # Both unique fields are reported: the slug is derived from the title, so a
    # duplicate title brings a duplicate slug with it.
    assert sorted(form.errors) == ['slug', 'title'], form.errors


@pytest.mark.parametrize('text,expected', [
    ('Kevätesikko ähkyssä', 'Kevatesikko ahkyssa'),
    # Nothing to strip: the text has to come back unchanged, not merely be of
    # the right type.
    ('valkonarsissi kukassa', 'valkonarsissi kukassa'),
    ('', ''),
])
def test_remove_diacritics_returns_a_text_string(text, expected):
    """A text string by construction, on both Python versions.

    ``u''.join(...)`` returns one whatever the interpreter; the ``filter()``
    this replaced returned a string only on Python 2, and on Python 3 an
    iterator whose ``<filter object ...>`` repr ``slugify`` would have silently
    baked into every derived slug. See docs/issues/016.
    """
    result = remove_diacritics(text)
    assert isinstance(result, type('')), \
        'remove_diacritics returned {0!r}, not a text string'.format(result)
    assert result == expected


@pytest.mark.django_db
def test_a_saved_photo_gets_an_accent_free_slug(media_root):
    """The whole path issue 016 was about, end to end.

    ``remove_diacritics`` is only ever reached through ``clean()``, so this
    goes through the form the admin uses: an accented title in, a saved
    ``Photo`` out, and the slug PostgreSQL stores read back off it.
    """
    from django.core.files.uploadedfile import SimpleUploadedFile
    from kasvimuseo.tests.conftest import jpeg_bytes

    form = PhotoForm(
        data={'title': 'Kevätesikko ähkyssä',
              'slug': '',
              'caption': '',
              'crop_from': 'center',
              'date_added': '2026-07-29 12:00:00',
              'tags': ''},
        files={'image': SimpleUploadedFile('kevatesikko.jpg', jpeg_bytes(),
                                           content_type=str('image/jpeg'))})

    assert form.is_valid(), form.errors
    photo = form.save()

    assert photo.slug == 'kevatesikko-ahkyssa'


# -- the instructions on the upload form (issue 037) --------------------------

@pytest.mark.django_db
def test_photo_form_says_what_to_name_the_file():
    """The rule the receiver matches on, stated where the file is chosen."""
    help_text = '{0}'.format(PhotoForm().fields['image'].help_text)

    assert 'suomenkielisen nimen' in help_text
    assert 'otsikon ensimmäinen sana' in help_text
    # And what happens when no species matches, which is silent otherwise.
    assert 'eikä näy millään lajilla' in help_text


@pytest.mark.django_db
def test_photo_form_says_that_a_blank_title_is_normal():
    help_text = '{0}'.format(PhotoForm().fields['title'].help_text)

    assert 'Voit jättää tämän tyhjäksi' in help_text
    # The file names are marked up, since the admin renders help_text
    # through ``|safe``.
    assert ('tiedoston nimi ilman <code>jpg</code>-, <code>jpeg</code>- '
            'tai <code>jpe</code>-päätettä') in help_text


@pytest.mark.django_db
def test_species_form_offers_only_this_species_photos(photo_factory):
    species = create_species(name_fi='Valkonarsissi')
    photo_factory(title='valkonarsissi kukassa')
    photo_factory(title='keltanarsissi')

    photos = SpeciesForm(instance=species).fields['photo'].queryset

    assert [photo.title for photo in photos] == ['valkonarsissi kukassa']


@pytest.mark.django_db
def test_species_form_keeps_the_photo_the_species_already_has(photo_factory):
    """A photo renamed away from the species is still on the list.

    Otherwise opening the form and saving it would drop the photo without
    anybody choosing to.
    """
    species = create_species(name_fi='valkonarsissi')
    species.photo = photo_factory(title='mummon narsissi')
    species.save()

    photos = SpeciesForm(instance=species).fields['photo'].queryset

    assert [photo.title for photo in photos] == ['mummon narsissi']


@pytest.mark.django_db
def test_species_form_says_what_the_photo_field_does():
    help_text = '{0}'.format(SpeciesForm().fields['photo'].help_text)

    assert 'Tyhjä irrottaa kuvan lajilta' in help_text
    # The one thing the field cannot promise: the receiver still wins.
    assert 'kuvan tallentaminen uudelleen kumoaa tämän valinnan' in help_text
