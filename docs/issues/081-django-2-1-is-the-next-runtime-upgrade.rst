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

Staging deployment
------------------

This section is for deployment operators. It records the Stage 12 deployment to ``kasvimuseo-staging.vempai.men`` on 2026-09-27.

Use ``README.rst``, "Updating code on the server", with ``ansible/hosts.staging`` and ``ansible/vars/staging.yml``.
Issue 079, "Staging deployment", describes archive creation and the required backups.

User checks
~~~~~~~~~~~

#. Open ``https://kasvimuseo-staging.vempai.men/kasvimuseo/planted-species/``.
#. Sign in at ``/admin/`` with a staging account.
#. Open the species, observation, photo and gallery lists.
#. Sign out at ``/accounts/logout/``.

Deployment results
~~~~~~~~~~~~~~~~~~

The deployment used the archive from branch commit ``b9d7bdf``, which includes runtime commit ``1b9b93e``.
The archive lives at ``/home/kasvimuseo/releases/issue081-1b9b93e/ylaneenkasvit-0.2.1.dev0.tar.gz`` on the staging host.
Its SHA-256 is ``37fdfc35730bc9a6dc7339bf4d0fdcd937e2e6c8b8cb4901de14867fb80b0900``.

* Ansible's ``code`` deployment reported ``ok=13 changed=4 failed=0`` and restarted ``ylaneenkasvit-wsgi``.
* The host runs the requested package versions on Python 3.7.3.
  ``pip check``, the system check and the scoped migration check passed.
* Django applied ``admin.0003_logentry_add_action_flag_choices`` and ``photologue.0011_auto_20190223_2138``.
  All 31 migrations are applied, with none pending.
* Counts stayed at 156 species, 311 observations and 137 photos.
* Public species, gallery and login pages answered HTTP 200 over HTTPS.
  Admin login, five authenticated pages, static CSS and logout passed.

The backup directory is ``/home/kasvimuseo/stage12-backup-20260927`` on staging.
It holds the database dump, previous Python environment and ``uwsgi.ini``.
Deployment logs live in the task worktree's ``.dev/issue081/deploy/`` directory.
