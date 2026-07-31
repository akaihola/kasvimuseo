# -*- coding: utf-8 -*-
"""Build the data the label editor tests arrange, inside the app container.

Python 2.7 and Django 1.5, because it runs where the application runs -- the
browser tests themselves are Python 3 on the host, and never import Django.
``dev/kasvimuseo app browser-test`` runs this against a throwaway database of
its own, so it drops what it made first and can be re-run.

The shape matters to the tests, so it is stated here rather than in six
fixtures:

* ``valkonarsissi`` has **two** plantings, museum numbers 11 and 12, so its one
  label carries two numbers that can be dragged apart, and **two** photos whose
  titles name it, so the label's chevrons have somewhere to go.
* ``kevätesikko`` has one planting, number 21, and one photo. It is the label
  that must *not* change when the first one does.
* ``sinivuokko`` is planted in a private bed, so it must not appear at all.
"""

from __future__ import unicode_literals

import io
import os
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from photologue.models import Photo, PhotoSize, PhotoSizeCache

from kasvimuseo import models
from kasvimuseo.tests import factories


def jpeg_bytes(width, height, color):
    buffer = io.BytesIO()
    Image.new(str('RGB'), (width, height), color).save(buffer, str('JPEG'))
    return buffer.getvalue()


def create_photo(title, width, height, color):
    """A photologue photo backed by a real file, named so it names a species.

    ``autoconnect_photo_to_species`` matches the first word of the title
    against ``Species.name_fi``, which is what puts the photo among the
    label's alternatives, and every save re-attaches -- so the photo created
    last is the one the species points at (issue 042).
    """
    name = '{0}.jpg'.format(title.replace(' ', '-'))
    photo = Photo(title=title, title_slug=title.replace(' ', '-'))
    photo.image.save(name,
                     SimpleUploadedFile(name,
                                        jpeg_bytes(width, height, color),
                                        content_type=str('image/jpeg')),
                     save=False)
    photo.save()
    return photo


def wipe():
    from django.conf import settings
    for model in (models.Label, models.Care, models.Planting,
                  models.Observation, models.Species, models.Bed,
                  models.Plot, models.Location):
        model.objects.all().delete()
    Photo.objects.all().delete()
    if os.path.isdir(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT)


def main():
    wipe()
    # ``get_display_url`` is the URL the labels render, and the accessor only
    # exists when a ``PhotoSize`` of that name is in the database. syncdb loads
    # photologue's own initial data, so this is a safety net for a database
    # built some other way, not a second definition.
    PhotoSize.objects.get_or_create(name='display',
                                    defaults={'width': 300, 'height': 300})
    PhotoSizeCache().reset()

    public = factories.create_bed(name='1', public=True)
    private = factories.create_bed(name='2', public=False)

    narsissi = factories.create_species(name_fi='valkonarsissi',
                                        external_id=1,
                                        genus='Narcissus',
                                        species='poeticus')
    for external_id in (11, 12):
        factories.create_planting(
            observation=factories.create_observation(species=narsissi,
                                                     external_id=external_id),
            bed=public)
    # Landscape and portrait, so the aspect handler has both to choose from.
    create_photo('valkonarsissi kukassa', 400, 300, (40, 120, 40))
    create_photo('valkonarsissi lehdet', 300, 400, (120, 40, 40))

    esikko = factories.create_species(name_fi='kevätesikko',
                                      external_id=2,
                                      genus='Primula',
                                      species='veris')
    factories.create_planting(
        observation=factories.create_observation(species=esikko,
                                                 external_id=21),
        bed=public)
    create_photo('kevätesikko niityllä', 400, 300, (40, 40, 120))

    vuokko = factories.create_species(name_fi='sinivuokko',
                                      external_id=3,
                                      genus='Hepatica',
                                      species='nobilis')
    factories.create_planting(
        observation=factories.create_observation(species=vuokko,
                                                 external_id=31),
        bed=private)

    print('seeded {0} species, {1} plantings, {2} photos'.format(
        models.Species.objects.count(),
        models.Planting.objects.count(),
        Photo.objects.count()))


if __name__ == '__main__':
    main()
