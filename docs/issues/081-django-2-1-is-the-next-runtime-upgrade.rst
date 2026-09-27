Issue 081: Django 2.1 is the next runtime upgrade step
======================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 12
:Evidence: Both images build on Python 3.7.17. All 531 tests, package checks, the system check and the scoped migration check pass.
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 12 with Django 2.1.15, Grappelli 2.12.4 and Photologue 3.9. Keep Python 3.7.
:Resolution: 1b9b93e updates the runtime pins and regenerates both locks.

Problem
=======

Stage 11 left the project on Django 2.0.13. Stage 12 of :doc:`../upgrade-plan` moves it to
Django 2.1.15. That stage also needs compatible Grappelli and Photologue pins.

Work
----

Update the runtime pins in ``requirements/production.in``,
``requirements/production.txt`` and ``requirements/dev.txt``. Use Django
2.1.15, Grappelli 2.12.4 and Photologue 3.9. Keep Python 3.7. Stage 12's
``login`` and ``logout`` removals were handled in Stage 9; do not repeat that
work.

Checks
------

This section is for reviewers. It records the commands and results for Stage 12.

Run these commands from the repository root::

    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue081
    export KASVIMUSEO_PG_PORT=5781
    export KASVIMUSEO_DB_NAME=issue081
    dev/kasvimuseo app build
    podman build -t kasvimuseo-prod-issue081 -f Dockerfile .
    podman run --rm kasvimuseo-dev-issue081 pip check
    podman run --rm kasvimuseo-prod-issue081 pip check
    dev/kasvimuseo app test
    dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo docs

Results on 2026-09-27:

* Both images built successfully and matched every applicable lock entry.
  Both run Python 3.7.17 and pass ``pip check``.
* All 531 tests passed in 20.30 seconds.
  Nine warnings concern Photologue's deprecated Pillow ``ANTIALIAS`` constant.
* The documentation build passed with warnings treated as errors.
* The system check found no issues.
  The scoped migration check found no changes in ``kasvimuseo``.
* Photologue 3.9 adds ``0011_auto_20190223_2138``, which changes the help text for ``PhotoEffect.filters``.
  The suite creates its database with the installed migrations.

The locks retain sortedm2m 1.5.0 and ExifRead 2.1.2.
Photologue 3.9's package metadata accepts these versions, despite the newer pins in the upgrade plan's Appendix A.
Issue 077, "Checks", owns the lock generation command.
This change ran that command with pip-tools 6.14.0 under Python 3.7 for the production and development locks.

The validation logs live in the task worktree's ``.dev/issue081/`` directory.
