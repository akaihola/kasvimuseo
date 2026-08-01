"""Empty on purpose, and no longer for fixtures.

This package used to carry ``fixtures/initial_data.json``, and a fixture is
only found in a package that has a ``models.py`` and is in
``settings.INSTALLED_APPS`` -- which is what this module was for. The fixture
now lives in ``kasvimuseo/fixtures/`` instead, because ``kasvimuseo`` has South
migrations and ``ylaneenkasvit`` has none: South loads a migrated application's
initial data after migrating it, while ``syncdb`` was loading this one before
South had created the photologue tables it names, and failing (issue 055).

The package stays in ``INSTALLED_APPS`` for ``ylaneenkasvit/locale/``, which
there is no ``LOCALE_PATHS`` entry to find it by.
"""
