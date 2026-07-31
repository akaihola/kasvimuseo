=========================================================
Issue 036: The runtime stack is end-of-life and unpatched
=========================================================

:Status: Open
:Severity: High
:Area: platform / security
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: 016, 019, 020, 021, 022, 023, 024, 027, 028, 029, 030, 031, 032, 033, 034 -- the individual obstacles, listed by stage under Progress below
:Blocks: (none)
:Related: 035 -- the ceiling that will make this recur
    040 -- option 3 there is to wait for this
    038 -- most of the documentation build's workarounds fall away at Stage 10
    018 -- CI has to run the project's own container until Stage 10
:Decision: undecided
:Resolution: (none yet)

Problem
=======

The application runs on **Python 2.7** and **Django 1.5.1**.

* Python 2.7 reached end of life on 1 January 2020.
* Django 1.5 stopped receiving security support in 2014. The current release is
  6.0.7; the pinned version is 1.5.1, and even 1.5.12 -- the last patch in that
  series, with the security fixes -- was never applied.
* ``python:2.7-alpine``, the base image, has had no updates since 2020, which
  includes the C libraries it links against.
* ``psycopg2-binary``, ``Pillow`` and the rest are pinned at similarly old
  versions.

This is the umbrella issue for the whole modernisation. The work is planned in
detail in **``docs/upgrade-plan.rst``**: 20 stages, from removing dead
dependencies through to Django 6.0 on Python 3.12, with the constraints,
per-stage lock files and code changes each one forces.

Impact
======

Unpatched security vulnerabilities across the entire stack, in an application
that is on the public internet and holds an admin login. No individual CVE is
called out here because the surface is the whole runtime, not one component.

Beyond security: the project cannot use current tooling, cannot run on current
CI images, and every new dependency has to be checked for Python 2 support --
which almost nothing has any more.

Options
=======

Follow ``docs/upgrade-plan.rst``. Its structure, in brief:

============ ======================================================
Stages 0-1   Dead weight and defensive settings; Django 1.5.12
Stages 2-4   photologue forward, still on Django 1.5/1.6
Stage 5      **South to Django migrations** -- the riskiest step
Stages 6-9   Django 1.7 to 1.11 LTS, the staging point
Stage 10     **Python 2.7 to 3.7** -- the irreversible one
Stages 11-19 Django 2.0 to 6.0, one version at a time
============ ======================================================

Suggested holding points are the LTS releases: 1.11 (before the Python flip),
2.2, 3.2, 4.2 and 5.2. Each is somewhere the project can sit indefinitely if
the work has to pause.

The effort is concentrated in four places: the South migration conversion
against real data, the Python 2 to 3 flip, the photologue ``title_slug`` rename
plus sites framework, and the recurring ``kasvimuseo_admin_list.py`` re-sync
(issue 034). Everything else is mechanical.

Progress
========

No stage started. Three obstacles are out of the way: 019 is ``Fixed``, so
``MIDDLEWARE_CLASSES`` is now written out in ``common_settings`` and Stage 11
has a list to rename rather than an absence to notice; 023 is ``Fixed`` with it,
so ``django.contrib.messages`` is installed and Stage 5 will not meet an admin
system check it fails; and 016 is ``Fixed``, so Stage 10's source work no longer
includes the ``filter()`` that would have corrupted every derived photo slug.
This issue tracks the programme; the individual obstacles have their own issues:

============ ===========================================================
Issue        Blocks or complicates
============ ===========================================================
019          MIDDLEWARE -- fixed; Stage 8 renames an explicit list
023          contrib.messages -- fixed; the app is installed for Stage 5
024          ``TEMPLATE_DIRS`` path -- fixed; Stage 10 has one item less
016          ``remove_diacritics`` -- fixed; Stage 10 has nothing to do here
027          No upper bounds -- every stage needs a real lock
028, 029     Pillow and setuptools ceilings on specific stages
030          Early stages need a period-appropriate build image
034          Recurring cost at all 19 Django steps; decide before Stage 6
035          The ceiling that will cause this to recur
============ ===========================================================

What is verified, and what is not
==================================

Verified: the constraints between packages, and that the far end works --
Django 6.0.7 with grappelli 5.0.0 and photologue 3.20 starts, passes
``manage.py check`` and has no pending migrations, as does the Django 5.2
equivalent.

**Not** verified: any of it against this project's own code or database.
``podman`` was unavailable, so the container was never built, no migration was
run and no page was rendered. Stage 0 should be treated as a test of the
reasoning, not as a foregone conclusion.
