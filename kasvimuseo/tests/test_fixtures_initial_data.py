# -*- coding: utf-8 -*-
"""Tests for where ``initial_data.json`` lives (issue 055).

The fixture names ``photologue.photosize`` rows, and photologue's tables are
South's. Two loaders can install it, and only one of them runs late enough:

* ``syncdb`` loads the initial data of the applications it syncs, which are the
  ones **without** migrations, and it runs before South has created anything.
  While the fixture sat in ``ylaneenkasvit`` -- a migration-less package that
  existed for no other purpose -- that is the loader it got, and it died on the
  first row with ``relation "photologue_photosize" does not exist``. Nothing
  loaded it afterwards, so a database built by ``dev/kasvimuseo db bootstrap``
  had no photo sizes at all and every photo rendered ``src=""``.
* South loads a migrated application's initial data **after** migrating it, by
  which time the tables exist. That is the loader the fixture has now, from
  living in ``kasvimuseo``.

**These tests do not exercise that.** The test database takes the
``SOUTH_TESTS_MIGRATE = False`` path, where ``syncdb`` creates every table at
once and the fixture therefore loads cleanly wherever it sits -- which is
exactly why the suite never saw the defect and cannot see it now. What they
pin is the one property the two loaders differ on, which is static: the
application the fixture belongs to has migrations. A move back to a
migration-less application fails the second test below, and the bootstrap
itself is verified by hand, in the issue.
"""

from __future__ import unicode_literals

import json
import os

from django.conf import settings
from django.db.models import loading
from django.utils.importlib import import_module

FIXTURE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))), 'fixtures', 'initial_data.json')


def app_directory(app_label):
    return os.path.dirname(import_module(app_label).__file__)


def has_migrations(app_label):
    """What South asks of an application before it migrates it."""
    return os.path.isdir(os.path.join(app_directory(app_label), 'migrations'))


def installed_apps_with_an_initial_data_fixture():
    for app_label in settings.INSTALLED_APPS:
        path = os.path.join(app_directory(app_label), 'fixtures',
                            'initial_data.json')
        if os.path.exists(path):
            yield app_label


def test_the_initial_data_fixture_is_kasvimuseos():
    assert os.path.exists(FIXTURE)
    assert list(installed_apps_with_an_initial_data_fixture()) == ['kasvimuseo']


def test_every_initial_data_fixture_is_in_a_migrated_application():
    """The property the bootstrap depends on, for whatever fixtures exist.

    Written over every installed application rather than over ``kasvimuseo``
    alone, because the failure this issue describes is not "the file moved" but
    "the file is somewhere ``syncdb`` will try it": a second fixture added to
    any migration-less application would reintroduce it.
    """
    for app_label in installed_apps_with_an_initial_data_fixture():
        assert has_migrations(app_label), (
            '{0}/fixtures/initial_data.json would be loaded by syncdb, before '
            'South has created the tables it names'.format(app_label))


def test_ylaneenkasvit_has_no_fixtures_and_no_migrations():
    """The pairing that made this a defect, stated from the other end.

    ``ylaneenkasvit`` is in ``INSTALLED_APPS`` for its ``locale/`` directory
    now; it defines no models. If it ever gains migrations the assertion below
    is the wrong guard rather than a broken one -- the one above is the guard.
    """
    directory = app_directory('ylaneenkasvit')

    assert not os.path.isdir(os.path.join(directory, 'fixtures'))
    assert not has_migrations('ylaneenkasvit')
    assert loading.get_models(loading.get_app('ylaneenkasvit')) == []


def test_the_fixture_ships_the_four_photo_sizes_production_has():
    """The file itself, without a database.

    ``test_templates.py`` asserts the rows are in the test database; this
    asserts what is in the file, which is what a bootstrapped database gets
    through South. The values are the production dump's -- see issue 054.
    """
    with open(FIXTURE) as fixture_file:
        rows = json.load(fixture_file)

    assert [row['model'] for row in rows] == ['photologue.photosize'] * 4
    assert [(row['pk'], row['fields']['name']) for row in rows] == [
        (1, 'admin_thumbnail'),
        (2, 'thumbnail'),
        (3, 'display'),
        (4, 'mobilethumbnail')]
