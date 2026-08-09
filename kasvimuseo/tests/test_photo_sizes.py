# -*- coding: utf-8 -*-
"""Tests for where the photo sizes come from (issues 054 and 055).

They were ``kasvimuseo/fixtures/initial_data.json`` until upgrade plan
Stage 5. Django 1.7 loads no ``initial_data`` fixture for an application with
migrations, so the rows moved into the data migration
``kasvimuseo/migrations/0002_photo_sizes.py``. The test database is built by
the migrations, so asserting the rows here asserts that the migration ran --
and ran before photologue's own ``0002_photosize_data``, which would otherwise
have filled the empty table with photologue's three default sizes.
"""

from __future__ import unicode_literals

import os

import pytest
from django.apps import apps


@pytest.mark.django_db
def test_the_migrations_create_the_four_photo_sizes_production_has():
    """The values are the production dump's -- see issue 054.

    Exactly these four rows: photologue's defaults -- an ``admin_thumbnail``
    of 100x75 among them -- must not appear beside or instead of them.
    """
    from photologue.models import PhotoSize

    rows = PhotoSize.objects.order_by('pk').values_list(
        'name', 'width', 'height', 'crop', 'upscale', 'quality')

    assert list(rows) == [
        ('admin_thumbnail', 51, 36, True, False, 70),
        ('thumbnail', 128, 128, False, False, 70),
        ('display', 352, 352, False, False, 70),
        ('mobilethumbnail', 80, 45, True, True, 80)]


def test_no_application_ships_an_initial_data_fixture():
    """From Django 1.7 on, ``initial_data`` is dead weight (issue 055).

    For an application with migrations nothing loads it, so a fixture by that
    name would sit in the tree looking load-bearing and doing nothing. The
    photo sizes above are a data migration for exactly that reason.
    """
    offenders = [
        app.label for app in apps.get_app_configs()
        if os.path.exists(os.path.join(app.path, 'fixtures',
                                       'initial_data.json'))]

    assert offenders == []
