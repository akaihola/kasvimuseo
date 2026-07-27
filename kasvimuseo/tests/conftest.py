# -*- coding: utf-8 -*-
"""Fixtures shared by the whole suite."""

from __future__ import unicode_literals

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


def jpeg_bytes(width=8, height=8, color=(0, 128, 0)):
    """A real, decodable JPEG.

    The printable and compact report templates make Django open the image to
    read its dimensions, so those tests need actual image data rather than a
    placeholder file.
    """
    from PIL import Image
    buffer = io.BytesIO()
    Image.new(str('RGB'), (width, height), color).save(buffer, str('JPEG'))
    return buffer.getvalue()


@pytest.fixture
def media_root(settings, tmpdir):
    """Point ``MEDIA_ROOT`` at a per-test temporary directory."""
    settings.MEDIA_ROOT = str(tmpdir)
    return str(tmpdir)


@pytest.fixture
def photo_factory(media_root):
    """Return a builder for photologue ``Photo`` objects backed by real files."""
    from photologue.models import Photo

    def create_photo(title='valkonarsissi kukassa', width=8, height=8):
        photo = Photo(title=title, title_slug=title.replace(' ', '-'))
        photo.image.save(
            '{0}.jpg'.format(title.replace(' ', '-')),
            SimpleUploadedFile('{0}.jpg'.format(title.replace(' ', '-')),
                               jpeg_bytes(width, height),
                               content_type=str('image/jpeg')),
            save=False)
        photo.save()
        return photo

    return create_photo
