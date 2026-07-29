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
def media_root(tmpdir):
    """Point ``MEDIA_ROOT`` at a per-test temporary directory.

    ``FileSystemStorage`` resolves ``MEDIA_ROOT`` once, when it is built, so
    ``default_storage`` keeps writing to the old directory unless it is
    rebuilt. Django does that from a ``setting_changed`` receiver -- but
    pytest-django's ``settings`` fixture only monkeypatches the settings object
    and never sends the signal, so go through ``override_settings``, which
    does.
    """
    from django.test.utils import override_settings
    override = override_settings(MEDIA_ROOT=str(tmpdir))
    override.enable()
    yield str(tmpdir)
    override.disable()


@pytest.fixture
def photo_factory(media_root):
    """Return a builder for photologue ``Photo`` objects backed by real files."""
    from photologue.models import Photo

    def create_photo(title='valkonarsissi kukassa', width=8, height=8,
                     filename=None):
        """Build a ``Photo``.

        ``filename`` defaults to the title, which is how the photographs in
        this database are usually named -- but only usually, and the two are
        read by different code: the title chooses the species, the file name
        tells namesakes apart. Tests that care about the difference pass both.
        """
        photo = Photo(title=title, title_slug=title.replace(' ', '-'))
        name = '{0}.jpg'.format(filename or title.replace(' ', '-'))
        photo.image.save(
            name,
            SimpleUploadedFile(name,
                               jpeg_bytes(width, height),
                               content_type=str('image/jpeg')),
            save=False)
        photo.save()
        return photo

    return create_photo
