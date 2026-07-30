# -*- coding: utf-8 -*-
"""Fixtures shared by the whole suite."""

from __future__ import unicode_literals

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


def jpeg_bytes(width=8, height=8, color=(0, 128, 0)):
    """A real, decodable JPEG.

    Photologue measures and resizes what is uploaded, and ``Species.save()``
    measures it again to store the orientation the reports render from, so
    these tests need actual image data rather than a placeholder file.
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


@pytest.fixture
def image_opens(monkeypatch):
    """Record every image file a piece of code opens, and return the list.

    Issue 011 is about a template that opened one; asserting it no longer does
    means watching the two doors an image can come through. Django reads
    ``ImageFieldFile.width`` by calling ``FieldFile.open()``, which goes to the
    storage, and photologue builds its cached sizes with ``PIL.Image.open`` on
    the path, which does not. Patching one alone would prove nothing.
    """
    from PIL import Image
    from django.core.files.storage import FileSystemStorage

    opened = []
    image_open, storage_open = Image.open, FileSystemStorage._open

    def record_image_open(fp, *args, **kwargs):
        opened.append(getattr(fp, 'name', fp))
        return image_open(fp, *args, **kwargs)

    def record_storage_open(self, name, mode='rb'):
        opened.append(name)
        return storage_open(self, name, mode)

    monkeypatch.setattr(Image, str('open'), record_image_open)
    monkeypatch.setattr(FileSystemStorage, str('_open'), record_storage_open)
    return opened


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
