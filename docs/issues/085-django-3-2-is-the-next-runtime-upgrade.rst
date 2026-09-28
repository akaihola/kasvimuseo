Issue 085: Django 3.2 is the next runtime upgrade step
======================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 16
:Evidence: Both images match their locks. The suite, browser checks, and migration checks pass; see "Checks".
:Depends on: 084
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 16 on Python 3.10.19 with the requested package pins. Keep implicit primary keys as AutoField.
:Resolution: 0e277fa upgrades the runtime and pins the implicit primary-key type.

Work
----

This issue is for the implementation agent. It tracks Stage 16 of :doc:`../upgrade-plan`.

Move the project to Django 3.2.25 after issue 084. Set
``DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'`` explicitly to prevent
Django 6.0 from changing the primary-key type. Update Grappelli to 2.15.7,
Photologue to 3.14, django-extensions to 3.1.5, and pytest-django to 4.5.2.
Move Python to 3.10 and keep the package locks in step with the pins.

Checks
------

This section records commands and results for reviewers.
Run these commands from the task checkout::

    export SHELL=/bin/bash
    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue085
    export KASVIMUSEO_PG_PORT=5785
    export KASVIMUSEO_DB_NAME=issue085
    dev/kasvimuseo app build
    podman build -t kasvimuseo-prod-issue085 -f Dockerfile .
    python3 .dev/issue085/check_packages.py
    dev/kasvimuseo app coverage
    dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage shell --settings=ylaneenkasvit.test_settings -c 'import runpy; runpy.run_path(".dev/issue085/check_primary_keys.py")'
    dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --noinput --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage showmigrations --plan --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app browser-test --engine chromium
    dev/kasvimuseo app browser-test --engine webkit
    dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py
    dev/kasvimuseo docs --clean
    python3 .dev/issue085/check_tracker.py
    git diff --check
    git diff master --name-only -- docs/issues/
    git status --short --untracked-files=all -- docs/issues/

The checks use this checkout's PostgreSQL cluster and temporary test media.
The scripts, inventories, and logs live in ``.dev/issue085/``.
The package comparison checks exact versions, missing packages, and unexpected packages.
It permits only packaging tools and the installed production application as extras.

Lock generation
~~~~~~~~~~~~~~~

This section records the resolver environment for package maintainers.
Issue 077, "Checks", owns the lock generation command and order.

The disposable resolver uses ``python:3.10.19-alpine3.22`` and the development image's build dependencies.
It installs pip 23.1.2, setuptools 57.5.0, wheel 0.41.3, pip-tools 6.14.0, and Click 8.1.8.
Click 8.5.0 generated false command options, including ``--no-index`` and ``--cert=None``.
Click 8.1.8 generated the correct command headers.

All three locks were regenerated on Python 3.10.19.
The generated locks own the installed versions.
The runtime pins also include django-sortedm2m 3.1.1, as Stage 16 requires.
The development lock drops ``six`` because django-extensions no longer requires it.
The test package versions remain unchanged.

Results
~~~~~~~

This section records the completed runtime checks on 2026-09-28, Helsinki time.

* The full suite passed through ``app coverage``. Coverage reached 99.52%, above the 97% gate.
* Both images built and report Python 3.10.19. Both passed ``pip check``.
* All 13 production packages and 23 development/test packages match their locks.
  The development image contains the packaging tools named in "Lock generation".
  The production image retains its base's pip 23.0.1, setuptools 79.0.1, and wheel 0.45.1.
  Its only other extra package is the installed application.
* Django's system check passed with the existing ``NullBooleanField`` deprecation warning.
  It emitted no ``models.W042`` warning.
* The settings check found the explicit ``AutoField`` value and checked all 11 implicit application primary keys.
  The scoped migration check found no model changes.
  All 34 migrations applied, with none pending.
* Chromium passed all 35 checks. WebKit passed 28 checks and skipped seven Chromium-only checks.
* All 78 issue-register and commit-reference tests passed again after rebasing onto local ``master``.
* The documentation build passed with warnings treated as errors and produced ``.dev/docs/html/index.html``.

The development image is ``d1b93349de6a``; the production image is ``633ba8d8f63d``.
The package audit initially expected the builder's packaging tools in the production image.
The base image inventory established the correct versions, and the corrected audit passed.

The rebase changed the runtime commit identifier, so the resolution field names its rewritten commit.
The tracker audit found only this issue changed against local ``master``.
Every other issue document matches ``master`` exactly.

Deployment prerequisite
------------------------

This section identifies the remaining work for the deployment operator.
Prepare a Python 3.10 target with a matching uWSGI interpreter before deploying this runtime.
The current Ansible configuration still selects Debian 11 and Python 3.9.
Issue 084, "Deployment attempt", records the staging host's older runtime and rejected deployment check.
The deployment operator owns target preparation and the Ansible transition.
These local image checks do not establish a successful live deployment.

Review checks
-------------

This section records the implementation review for maintainers.
Use the environment from "Checks" and run::

    dev/kasvimuseo app test kasvimuseo/tests/test_database_timezone.py kasvimuseo/tests/test_settings_session_serializer.py kasvimuseo/tests/test_admin.py kasvimuseo/tests/test_photologue_galleries.py kasvimuseo/tests/test_photos_integration.py kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py --disable-warnings
    python3 .dev/issue085/review_tracker.py
    podman run --rm kasvimuseo-prod-issue085 python -c 'from ylaneenkasvit import common_settings; assert vars(common_settings)["DEFAULT_AUTO_FIELD"] == "django.db.models.AutoField"'

All 125 focused tests passed.
Both image package comparisons passed again.
The repeated Django checks found no model changes or pending migrations.
The primary-key checks passed in the development environment and the installed production package.
The system check retained only the deprecation warning recorded in "Results".
The documentation build passed again.
The review found no implementation defect.

The register contains 85 issue files and 85 ranking entries.
Each issue appears under exactly one ranking heading.
The rendered queue contains one ready issue and 84 parked issues, with no overlap or duplicate rows.
Only issue 085 moved from "Ready now" to "Not in the queue" against local ``master``.
The audit script and logs live in ``.dev/issue085/review_tracker.py`` and ``.dev/issue085/review-*.log``.
