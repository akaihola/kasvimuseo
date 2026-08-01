# -*- coding: utf-8 -*-
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        """Give an existing database the ``mobilethumbnail`` photo size.

        ``reports/planted-species-list.html`` renders
        ``species.photo.get_mobilethumbnail_url``, and photologue attaches
        ``get_<size>_url`` only for the sizes that are rows in
        ``photologue_photosize``. The same change adds the row to
        ``ylaneenkasvit/fixtures/initial_data.json``, but that fixture is
        loaded at ``syncdb`` and never again, so a database that already
        exists would keep rendering ``src=""`` (issue 054).

        The values are the ones the production database has carried since the
        page was written -- 80x45, cropped, upscaled, quality 80 -- read out of
        the dump rather than invented. Production therefore already has this
        row and this migration does nothing there, which is the point of
        ``get_or_create``: it is the databases built from the fixture that need
        it.

        ``PhotoSize`` is imported from ``photologue.models`` rather than taken
        from ``orm``, because it belongs to another application and this
        migration only writes one row of data. Saving it clears
        ``PhotoSizeCache``, so a running process picks the accessor up.
        """
        from photologue.models import PhotoSize

        PhotoSize.objects.get_or_create(name='mobilethumbnail',
                                        defaults={'width': 80,
                                                  'height': 45,
                                                  'quality': 80,
                                                  'crop': True,
                                                  'upscale': True})

    def backwards(self, orm):
        """Nothing to undo.

        Deleting the row would break the page on every database, including the
        ones that had it before this migration ran.
        """

    models = {}

    complete_apps = []
    symmetrical = True
