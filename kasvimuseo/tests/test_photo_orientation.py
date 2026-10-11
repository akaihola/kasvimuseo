"""Tests for how photologue turns a phone photo upright (issue 089).

A phone stores a photo taken upright as a landscape image and an EXIF
``Orientation`` tag that says how to turn it. Photologue reads the tag when it
builds each cached size. From photologue 3.20 it reads the tag after it applies
a ``PhotoEffect``, and an enhanced or filtered image has no EXIF data left.

Issue 089 decided to accept the regression and to report it upstream. The
effect test pins the regression until a photologue release fixes it.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

#: The EXIF tag, and the value a phone writes when it was held upright.
ORIENTATION = 0x0112
RIGHT_TOP = 6


def sideways_jpeg_bytes():
    """A 40x20 JPEG that its EXIF data says to show as 20x40."""
    from PIL import Image
    exif = Image.Exif()
    exif[ORIENTATION] = RIGHT_TOP
    buffer = io.BytesIO()
    Image.new('RGB', (40, 20), (0, 128, 0)).save(
        buffer, 'JPEG', exif=exif.tobytes())
    return buffer.getvalue()


def display_size_of_a_sideways_photo(effect=None):
    """The size of the ``display`` rendition photologue builds for it."""
    from photologue.models import Photo
    photo = Photo(title='valkonarsissi kukassa', slug='valkonarsissi-kukassa',
                  effect=effect)
    name = 'valkonarsissi-kukassa.jpg'
    photo.image.save(
        name,
        SimpleUploadedFile(name, sideways_jpeg_bytes(),
                           content_type='image/jpeg'),
        save=False)
    photo.save()
    return photo.get_display_size()


@pytest.mark.django_db
def test_a_photo_with_no_effect_is_turned_upright(media_root, display_size):
    assert display_size_of_a_sideways_photo() == (20, 40)


@pytest.mark.django_db
def test_a_photo_with_an_effect_stays_sideways(media_root, display_size):
    """The defect of issue 089, pinned as it is today.

    Photologue 3.19 turned this photo upright too. A fix changes the expected
    size to ``(20, 40)``.
    """
    from photologue.models import PhotoEffect
    effect = PhotoEffect.objects.create(name='kontrasti', contrast=1.2)

    assert display_size_of_a_sideways_photo(effect) == (40, 20)
