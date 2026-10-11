Issue 084: Django 3.1 is the next runtime upgrade step
======================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 15
:Evidence: The PostgreSQL timestamp regression passes. Both images match their locks; see "Checks".
:Depends on: 083
:Blocks: 085
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 15 on Python 3.9 as requested. Use the compatible pins after checking both images and PostgreSQL.
:Resolution: 998114d upgrades the runtime and checks PostgreSQL timestamp decoding.

Work
----

This issue is for the implementation agent. It tracks Stage 15 of :doc:`../upgrade-plan`.

Move the project to Django 3.1.14 after issue 083. Confirm that the
``tzinfo_factory`` fix makes ``psycopg2-binary`` 2.9.x safe, then update
Grappelli to 2.14.4 and Photologue to 3.13. Keep the package locks in step
with the pins.

Timezone compatibility
----------------------

This section explains the driver boundary for runtime maintainers.

The database session remains UTC with ``USE_TZ=True`` and the application's ``TIME_ZONE='Europe/Helsinki'``.
With psycopg2 2.9.5, the cursor passes ``datetime.timedelta(0)`` to its timezone callback.
Django 3.0's callback compares that value with integer zero and raises its UTC assertion.
The diagnostic reproduced that failure with the old callback in the same UTC session.

Django 3.1's ``DatabaseWrapper.tzinfo_factory`` returns the connection timezone without that comparison.
The query returned ``2020-06-01T09:30:00+00:00`` for input ``2020-06-01T12:30:00+03:00``.
The regression in ``kasvimuseo/tests/test_database_timezone.py`` checks timezone awareness, the UTC offset, and the unchanged instant.

Session test compatibility
--------------------------

This section records the test changes for reviewers.

The first full suite run passed 530 tests and failed two session serializer tests.
Their helper decoded the old base64 session format directly.
Django 3.1 signs and compresses the session payload, so that decoder failed.

``stored_payload()`` now uses Django's signing API with an explicit JSON serializer.
It still reads the stored database row and rejects a non-JSON payload.
All three session serializer tests pass.

Checks
------

This section records commands and results for reviewers.
Run these commands from the task checkout::

    export SHELL="$(command -v bash)"
    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue084
    export KASVIMUSEO_PG_PORT=5784
    export KASVIMUSEO_DB_NAME=issue084
    dev/kasvimuseo app build
    podman build -t kasvimuseo-prod-issue084 -f Dockerfile .
    podman run --rm kasvimuseo-dev-issue084 pip check
    podman run --rm kasvimuseo-prod-issue084 pip check
    python3 .dev/issue084/check_packages.py
    dev/kasvimuseo app test kasvimuseo/tests/test_database_timezone.py
    dev/kasvimuseo app manage shell --settings=ylaneenkasvit.test_settings -c 'import runpy; runpy.run_path(".dev/issue084/check_timezone.py")'
    dev/kasvimuseo app test kasvimuseo/tests/test_settings_session_serializer.py --disable-warnings
    dev/kasvimuseo app coverage
    dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --noinput --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage showmigrations --plan --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app browser-test --engine chromium
    dev/kasvimuseo app browser-test --engine webkit
    dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py
    dev/kasvimuseo docs --clean
    python3 .dev/issue084/check_tracker.py
    git diff --check
    git diff main --name-only -- docs/issues

The checks use this checkout's PostgreSQL cluster and temporary test media.
The scripts, package inventories, and logs live in ``.dev/issue084/``.

Lock generation
~~~~~~~~~~~~~~~

This section identifies the resolver for package maintainers.
Issue 077, "Checks", owns the lock generation command and order.
The resolver used the Stage 14 image ``49d1a73521ee`` in a disposable container.
It used Python 3.9.25, pip 23.1.2, setuptools 57.5.0, wheel 0.41.3, and pip-tools 6.14.0.

All three locks were regenerated; the testing lock remained identical.
The production and development locks changed only the four requested package versions.
Photologue's metadata permits the existing ExifRead, Pillow, and django-sortedm2m pins.
The generated locks own the package versions.

Results
~~~~~~~

This section records the completed checks on 2026-09-28, Helsinki time.

* The full suite passed all 532 tests. Coverage reached 99.52%, above the 97% gate.
* Both images built and report Python 3.9.25. Both passed ``pip check``.
* All 13 production packages and 24 development/test packages match their locks.
  The only extra packages are packaging tools and the installed production application.
* Django's system check exited successfully with the ``NullBooleanField`` deprecation warning.
  The scoped migration check found no model changes. All 34 migrations applied, with none pending.
* Chromium passed all 35 browser checks.
  WebKit passed 28 checks and skipped seven Chromium-only touch checks.

* All 78 issue-register and commit-reference tests passed after rebasing onto local ``main``.
* The documentation build passed with warnings treated as errors.
  It produced ``.dev/docs/html/index.html``.
* The tracker audit found only this issue changed against ``main``.
  Every other tracker file matches ``main`` exactly, including the concurrent issue 085 addition.
  The runtime resolution commit remains reachable from this branch.

The development image is ``e3595ba82173``; the production image is ``0e1579914fb8``.
Later runtime stages own the Django and Pillow deprecations.

Review checks
-------------

This section records the implementation review for maintainers.
Use the environment from "Checks" and run::

    dev/kasvimuseo app test kasvimuseo/tests/test_database_timezone.py kasvimuseo/tests/test_settings_session_serializer.py kasvimuseo/tests/test_admin.py kasvimuseo/tests/test_photologue_galleries.py kasvimuseo/tests/test_photos_integration.py kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py --disable-warnings
    python3 .dev/issue084/check_packages.py
    python3 .dev/issue084/review_tracker.py
    dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo docs --clean

All 125 focused tests passed.
Both image package comparisons passed again.
The Django checks passed with the recorded deprecation warning and no pending migrations.
The review found no implementation defect.

The register contains 85 issue files and 85 ranking entries.
Each issue appears under exactly one ranking heading.
The generated queue contains two ready issues and 83 parked issues, with no overlap.
Issue 084 appears only in the parked section.
Every other tracker file matches ``main`` exactly.
The audit script and its results live in ``.dev/issue084/review_tracker.py`` and ``.dev/issue084/review-tracker.log``.

Deployment records
------------------

The private deployment repository owns deployment checks and operations results.
