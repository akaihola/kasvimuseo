Issue 079: Django 2.0 removes the last 1.x APIs this project uses
=================================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-15
:Source: Backlog refill from upgrade plan Stage 11
:Evidence: 531 tests pass on Django 2.0.13 with no ``RemovedInDjango`` warning; both images build; ``check`` and the scoped migration check pass.
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 11 on Python 3.7 with the pins the upgrade plan names. Keep the later stages in issue 036.
:Resolution: d1b5f89 drops the removed APIs; c07bab2 updates two tests; 3d4e3f1 moves the pins.

Work
----

This issue is for the implementation agent. It tracks Stage 11 of :doc:`../upgrade-plan`.

Django 2.0 removes three things the code still uses:

#. ``allow_tags`` on three ``ModelAdmin`` methods in ``kasvimuseo/admin.py``.
#. ``use_for_related_fields`` on ``ObservationManager`` in ``kasvimuseo/models.py``.
#. ``include(admin.site.urls)`` in ``ylaneenkasvit/urls.py``, a 3-tuple include.

The stage also moves the pins: Django 2.0.13, grappelli 2.11.2, photologue 3.8.1 and sortedm2m 1.5.0.
Python stays at 3.7.

Two removals the plan did not list were in the tests, not the application:
direct assignment to ``user_permissions`` and the loader's ``load_template_source``.
ExifRead stays at 2.1.2 because photologue 3.8.1 only requires that version.

Checks
------

This section is for reviewers. It records the commands the branch ran and their results.

Run these commands from the repository root::

    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 dev/kasvimuseo app build
    podman build -t kasvimuseo-stage11-prod -f Dockerfile .
    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 KASVIMUSEO_PG_PORT=5711 KASVIMUSEO_DB_NAME=stage11 dev/kasvimuseo app test
    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 KASVIMUSEO_PG_PORT=5711 KASVIMUSEO_DB_NAME=stage11 dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 KASVIMUSEO_PG_PORT=5711 KASVIMUSEO_DB_NAME=stage11 dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo docs

Results on 2026-09-15:

* The suite passed 531 tests in 22 seconds. The 10 remaining warnings are Python and Pillow deprecations inside Django and photologue.
* Both images report Django 2.0.13, grappelli 2.11.2, photologue 3.8.1, sortedm2m 1.5.0 and Python 3.7.17.
* ``check`` found no issues. ``makemigrations --check`` found no change in ``kasvimuseo``. photologue 3.8.1 ships the same ten migrations as 3.7.
* The locks were regenerated with issue 077's ``pip-compile`` command inside ``kasvimuseo-077-dev``.
