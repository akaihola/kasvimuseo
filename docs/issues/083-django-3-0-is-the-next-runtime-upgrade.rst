Issue 083: Django 3.0 is the next runtime upgrade step
======================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 14
:Evidence: All 531 tests pass. Both images match their locks; browser, system, migration and documentation checks pass.
:Depends on: 082
:Blocks: 084
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 14 on Python 3.9. Keep psycopg2-binary at 2.8.6 and remove obsolete Python 2 helpers.
:Resolution: c143913 upgrades the runtime and removes incompatible helpers.

Work
----

This issue is for the implementation agent. It tracks Stage 14 of :doc:`../upgrade-plan`.

Move the project to Django 3.0.14 after issue 082. Replace the three
``render_to_response`` calls with ``render(request, …)`` in
``kasvimuseo/views.py`` and remove the unused ``RequestContext`` import. Use
the PostgreSQL backend name supported by Django 3.0. Check whether any
remaining dependency uses ``django.utils.six``. Update Photologue to 3.11 and
Grappelli to 2.14.2. Keep ``psycopg2-binary`` below 2.9.

Compatibility changes
---------------------

This section tells reviewers which compatibility changes this stage needs.

Stage 8 already replaced the shortcut rendering calls and removed ``RequestContext``.
``planted_observation()`` uses ``render(request, ...)``.
``PlantedSpecies.get()`` uses ``TemplateResponseMixin.render_to_response()``, which Django 3.0 still supports.

The database setting now uses ``django.db.backends.postgresql``.
Three tests replaced ``django.utils.six`` with standard Python 3 behavior.
The logging test uses ``io.StringIO``; the development login tests use ``importlib.reload``.
The model string test checks Unicode strings directly.

The first suite run stopped during startup because Django 3.0 removed ``python_2_unicode_compatible``.
The model classes already define ``__str__`` methods, so this change removes their obsolete decorators and import.
The existing Finnish model string test checks the resulting behavior.

Checks
------

This section records the commands and results for reviewers.
Run these commands from the task checkout::

    export SHELL="$(command -v bash)"
    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue083
    export KASVIMUSEO_PG_PORT=5783
    export KASVIMUSEO_DB_NAME=issue083
    dev/kasvimuseo app build
    podman build -t kasvimuseo-prod-issue083 -f Dockerfile .
    podman run --rm kasvimuseo-dev-issue083 pip check
    podman run --rm kasvimuseo-prod-issue083 pip check
    podman run --rm kasvimuseo-dev-issue083 pip list --format=json
    podman run --rm kasvimuseo-prod-issue083 pip list --format=json
    dev/kasvimuseo app test
    dev/kasvimuseo app coverage
    dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --noinput --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage showmigrations --plan --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app browser-test --engine chromium
    dev/kasvimuseo app browser-test --engine webkit
    dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py
    dev/kasvimuseo docs --clean

The checks use this checkout's PostgreSQL directory and temporary test media.
The validation logs and package comparison script live in ``.dev/issue083/``.

Lock generation
~~~~~~~~~~~~~~~

This section identifies the resolver and its results for package maintainers.
Issue 077, "Checks", owns the lock generation command and order.
The resolver used issue 082's development image, ``3093387499cc``, in a disposable container.
It used Python 3.9.25, pip 23.1.2, setuptools 57.5.0, wheel 0.41.3, and pip-tools 6.14.0.
All three locks were regenerated; the testing lock remained identical.

The runtime now includes asgiref and typing-extensions.
Standalone ``six`` remains a development dependency of django-extensions.
The other compatible pins remain unchanged, including psycopg2-binary 2.8.6.

Results
~~~~~~~

This section records completed checks on 2026-09-27.

* All 531 tests passed. Coverage reached 99.52%, above the 97% gate.
* Both images built successfully and report Python 3.9.25 with Django 3.0.14.
* All 13 production packages and 24 development/test packages match their locks.
  Both images passed ``pip check``.
  The only additional packages are pip, setuptools, wheel, and the installed production application.
* A scan of Python import statements found no ``django.utils.six`` imports in either image's Python packages.
  The repository Python files also contain no remaining imports.
* Django's system check passed. The scoped migration check found no model changes.
  All 33 migrations applied, with none pending.
* All 78 issue-register and commit-reference checks passed after the rebase onto local ``master``.
* Chromium passed all 35 browser checks.
  WebKit passed 28 checks and skipped seven Chromium-only touch checks.
* The documentation build passed with warnings treated as errors.
  It produced ``.dev/docs/html/index.html``.

The development image is ``49d1a73521ee``; the production image is ``206526cfc510``.
The suite reports existing Pillow deprecations and Django APIs scheduled for later removal.
The later upgrade stages own those changes.

The tracker diff against ``master`` changes only this issue.
The branch contains separate runtime and validation commits.

Review checks
-------------

This section records the implementation review for maintainers.
Use the environment from "Checks" and run::

    dev/kasvimuseo app test kasvimuseo/tests/test_models.py kasvimuseo/tests/test_dev_login.py kasvimuseo/tests/test_settings_logging.py kasvimuseo/tests/test_views.py kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py
    python3 .dev/issue083/review_tracker.py

All 174 focused tests passed.
The review repeated the package comparisons and Django checks from "Checks" successfully.
It found no implementation defect.

The register contains 84 issue files and 84 ranking entries.
Each issue appears under exactly one ranking heading.
The generated queue contains two ready issues and 82 parked issues, with no overlap.
Issue 083 appears only in the parked section.
The tracker comparison against ``master`` found no changes to other issues.
The audit script and its results live in ``.dev/issue083/review_tracker.py`` and ``.dev/issue083/review-tracker.log``.

Deployment records
------------------

The private deployment repository owns deployment checks and operations results.
