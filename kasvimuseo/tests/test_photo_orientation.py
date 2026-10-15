"""Tests for how a phone photo is turned upright (issue 089).

A phone stores a photo taken upright as a landscape image and an EXIF
``Orientation`` tag that says how to turn it. From photologue 3.20, photologue
reads the tag after it applies a ``PhotoEffect``, and an enhanced or filtered
image has no EXIF data left (upstream issue 233).

Issue 089 decided to turn each uploaded original upright before photologue
stores it. ``turn_photo_upright`` in ``kasvimuseo/models.py`` does that. The
strict expected failure at the bottom pins the upstream regression without the
receiver. It fails when a photologue release fixes the order, which is the
signal for task 19.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL.ExifTags import IFD, Base

from kasvimuseo.tests.factories import create_species

#: The value a phone writes when it was held upright.
RIGHT_TOP = 6
TAKEN = '2026:05:01 10:00:00'
TITLE = 'valkonarsissi kukassa'


def tagged_image_bytes(orientation=RIGHT_TOP, image_format='JPEG'):
    """A 40x20 image whose EXIF data says to turn it by ``orientation``."""
    from PIL import Image
    exif = Image.Exif()
    exif[Base.Orientation] = orientation
    exif.get_ifd(IFD.Exif)[Base.DateTimeOriginal] = TAKEN
    buffer = io.BytesIO()
    Image.new('RGB', (40, 20), (0, 128, 0)).save(
        buffer, image_format, exif=exif.tobytes())
    return buffer.getvalue()


def save_photo(data, extension='jpg', effect=None, committed=True):
    """Save a ``Photo`` the way a test or the admin uploads one.

    ``committed`` stores the file before the save, as ``photo_factory`` does.
    Otherwise the field holds the upload, as after the admin form, and
    ``FileField.pre_save`` stores it.
    """
    from photologue.models import Photo
    photo = Photo(title=TITLE, slug='valkonarsissi-kukassa', effect=effect)
    name = f'valkonarsissi-kukassa.{extension}'
    upload = SimpleUploadedFile(name, data)
    if committed:
        photo.image.save(name, upload, save=False)
    else:
        photo.image = upload
    photo.save()
    return photo


def stored_bytes(photo):
    with photo.image.storage.open(photo.image.name, 'rb') as stored:
        return stored.read()


def stored_image(photo):
    from PIL import Image
    image = Image.open(io.BytesIO(stored_bytes(photo)))
    image.load()
    return image


@pytest.fixture
def without_the_receiver():
    """Disconnect ``turn_photo_upright`` for one test."""
    from django.db.models.signals import pre_save
    from photologue.models import Photo

    from kasvimuseo.models import turn_photo_upright
    assert pre_save.disconnect(turn_photo_upright, sender=Photo)
    yield
    pre_save.connect(turn_photo_upright, sender=Photo)


@pytest.mark.django_db
@pytest.mark.parametrize('committed', [True, False])
def test_a_sideways_jpeg_is_stored_upright(media_root, committed):
    species = create_species()

    photo = save_photo(tagged_image_bytes(), committed=committed)

    image = stored_image(photo)
    assert image.size == (20, 40)
    assert Base.Orientation not in image.getexif()
    assert photo.image.name == 'photologue/photos/valkonarsissi-kukassa.jpg'
    species.refresh_from_db()
    assert species.photo == photo
    assert species.photo_is_horizontal is False


@pytest.mark.django_db
def test_turning_a_stored_original_leaves_no_copy(media_root):
    photo = save_photo(tagged_image_bytes())

    assert photo.image.storage.listdir('photologue/photos')[1] == [
        'valkonarsissi-kukassa.jpg']


@pytest.mark.django_db
def test_the_stored_original_keeps_the_date_taken(media_root):
    photo = save_photo(tagged_image_bytes())

    exif = stored_image(photo).getexif().get_ifd(IFD.Exif)
    assert exif[Base.DateTimeOriginal] == TAKEN
    assert photo.date_taken is not None


@pytest.mark.django_db
@pytest.mark.parametrize('image_format, extension', [
    ('PNG', 'png'),
    ('JPEG', 'jpg'),
])
def test_an_upright_image_is_stored_as_uploaded(
        media_root, image_format, extension):
    data = tagged_image_bytes(1, image_format)

    photo = save_photo(data, extension)

    assert stored_bytes(photo) == data


@pytest.mark.django_db
def test_a_sideways_photo_with_no_effect_is_shown_upright(
        media_root, display_size):
    assert save_photo(tagged_image_bytes()).get_display_size() == (20, 40)


@pytest.mark.django_db
def test_a_sideways_photo_with_an_effect_is_shown_upright(
        media_root, display_size):
    from photologue.models import PhotoEffect
    effect = PhotoEffect.objects.create(name='kontrasti', contrast=1.2)

    photo = save_photo(tagged_image_bytes(), effect=effect)

    assert photo.get_display_size() == (20, 40)


@pytest.mark.django_db
def test_a_sideways_photo_with_a_size_effect_is_shown_upright(
        media_root, display_size):
    from photologue.models import PhotoEffect, PhotoSize
    size = PhotoSize.objects.get(name='display')
    size.effect = PhotoEffect.objects.create(name='kontrasti', contrast=1.2)
    size.save()

    photo = save_photo(tagged_image_bytes())

    assert photo.get_display_size() == (20, 40)


@pytest.mark.django_db
@pytest.mark.xfail(strict=True, reason='upstream issue 233')
def test_photologue_turns_a_photo_with_an_effect_upright(
        media_root, display_size, without_the_receiver):
    """The regression of issue 089, which the receiver works around.

    Photologue 3.19 passed this test. When a photologue release passes it
    again, the strict mark fails the suite. Task 19 then decides whether the
    receiver can go.
    """
    from photologue.models import PhotoEffect
    effect = PhotoEffect.objects.create(name='kontrasti', contrast=1.2)

    photo = save_photo(tagged_image_bytes(), effect=effect)

    assert photo.get_display_size() == (20, 40)
