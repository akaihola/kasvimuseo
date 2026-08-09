"""Empty on purpose, and no longer for fixtures.

This package used to carry ``fixtures/initial_data.json``, and a fixture is
only found in a package that has a ``models.py`` and is in
``settings.INSTALLED_APPS`` -- which is what this module was for. The fixture
moved to ``kasvimuseo/fixtures/`` (issue 055) and then out of the fixture form
altogether: since upgrade plan Stage 5 the rows are the data migration
``kasvimuseo/migrations/0002_photo_sizes.py``, because Django 1.7 loads no
``initial_data`` fixture for an application with migrations.

The package stays in ``INSTALLED_APPS`` for ``ylaneenkasvit/locale/``, which
there is no ``LOCALE_PATHS`` entry to find it by.
"""
