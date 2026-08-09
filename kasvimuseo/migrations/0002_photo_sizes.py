# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


# The four rows the production database carries, read out of the dump (issues
# 054 and 055). They were ``kasvimuseo/fixtures/initial_data.json`` until
# upgrade plan Stage 5: Django 1.7 loads no ``initial_data`` fixture for an
# application with migrations, so a data migration is what installs them now.
PHOTO_SIZES = [
    {'name': 'admin_thumbnail', 'width': 51, 'height': 36, 'crop': True,
     'upscale': False, 'pre_cache': False, 'increment_count': False,
     'quality': 70},
    {'name': 'thumbnail', 'width': 128, 'height': 128, 'crop': False,
     'upscale': False, 'pre_cache': False, 'increment_count': False,
     'quality': 70},
    {'name': 'display', 'width': 352, 'height': 352, 'crop': False,
     'upscale': False, 'pre_cache': False, 'increment_count': False,
     'quality': 70},
    {'name': 'mobilethumbnail', 'width': 80, 'height': 45, 'crop': True,
     'upscale': True, 'pre_cache': False, 'increment_count': False,
     'quality': 80},
]


def create_photo_sizes(apps, schema_editor):
    """Give a new database the photo sizes this application renders with.

    ``get_or_create`` by name, so a database that has a row -- production, or
    any database migrated before -- keeps it untouched.
    """
    PhotoSize = apps.get_model('photologue', 'PhotoSize')
    for values in PHOTO_SIZES:
        PhotoSize.objects.get_or_create(name=values['name'], defaults=values)


def delete_nothing(apps, schema_editor):
    """Nothing to undo.

    Deleting the rows would break every page that renders a photo, on every
    database, the ones that had the rows before this migration included.
    """


class Migration(migrations.Migration):

    dependencies = [
        ('kasvimuseo', '0001_initial'),
    ]

    # Before photologue's own data migration, which fills an *empty*
    # ``photologue_photosize`` table with photologue's three default sizes.
    # With this migration first the table is not empty, so a new database gets
    # exactly the four production rows and none of photologue's.
    run_before = [
        ('photologue', '0002_photosize_data'),
    ]

    operations = [
        migrations.RunPython(create_photo_sizes, delete_nothing),
    ]
