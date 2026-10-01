Issue 088: Django 6.0 is the next runtime upgrade
=================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 19
:Evidence: Both images match their locks. Application, browser, system, and migration checks pass; see "Results".
:Depends on: (none)
:Blocks: (none)
:Related: 036, 087 -- the runtime upgrade programme; 087 is Stage 18
:Decision: Upgrade directly to Django 6.0.7 on Python 3.12, keep ``AutoField``, and change only the dependency files.
:Resolution: ee9427d upgrades the runtime and package locks.

Work
----

This issue tracks Stage 19 of :doc:`../upgrade-plan`.

Move the project from Django 5.2 to Django 6.0.7 on Python 3.12 or later. Keep
``DEFAULT_AUTO_FIELD`` set to ``AutoField`` or plan the database change to
``BigAutoField``. Use ``psycopg2 >= 2.9.9`` or psycopg 3. Update Grappelli to
5.0.0 and Photologue to 3.20. Remove ExifRead from the production dependencies.
Keep ``django-extensions`` development-only because version 4.1 does not claim
Django 6.0 support.

Checks
------

Build both images. Confirm that their installed packages match the committed
locks. Run the application tests, browser tests, Django system check, migration
checks and documentation build. Record the commands and results here.

Implementation
--------------

This section explains the upgrade for maintainers.
The dependency inputs select Django 6.0.7, Grappelli 5.0.0, Photologue 3.20, and psycopg2-binary 2.9.12.
The production input no longer pins ExifRead, and Photologue 3.20 does not require it.
The resolved locks contain no ExifRead.
``django-extensions`` 3.2.3 remains in ``requirements/dev.in`` only.
Both container definitions retain Python 3.12.12.

``DEFAULT_AUTO_FIELD`` stays ``django.db.models.AutoField``, so the database needs no migration.
The source uses no API that Django 6.0 removes.
Grappelli 5.0.0 ships the same templates and jQuery files as 4.0.4.
The project's ``grappelli/dashboard/modules/link_list.html`` override therefore needs no change.
The upgrade requires no source, model, or migration edits.

Issue 087 is Stage 18, and this branch builds on its unmerged branch.
Issue 087 on ``master`` names no blocked issue.
This issue therefore lists 087 under ``Related``, not ``Depends on``, so the dependency graph stays symmetric.
Every other issue document remains identical to local ``master``, except the 087 file from its own branch.

Validation commands
-------------------

This section gives reviewers the environment and commands for the acceptance checks.
Run them from the task checkout::

    export SHELL="$(command -v bash)"
    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue088
    export KASVIMUSEO_DB_NAME=issue088_upgrade
    export KASVIMUSEO_PG_PORT=5788
    export KASVIMUSEO_BROWSER_DB_NAME=issue088_browsertest
    dev/kasvimuseo app build
    podman build -f Dockerfile -t kasvimuseo-prod-issue088 .
    python3 .dev/issue088/check_packages.py
    dev/kasvimuseo app coverage
    dev/kasvimuseo app test -q
    bash .dev/issue088/check_runtime.sh
    podman run --rm -i -e DJANGO_SETTINGS_MODULE=ylaneenkasvit.test_settings \
      kasvimuseo-prod-issue088 python < .dev/issue088/check_static.py
    dev/kasvimuseo app browser-test --engine chromium
    dev/kasvimuseo app browser-test --engine webkit
    dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py
    dev/kasvimuseo docs --clean
    git diff --check
    git diff master --name-only -- docs/issues/

Scripts, logs, and package inventories remain under ``.dev/issue088/`` in this task checkout.
:doc:`086-django-4-2-runtime-upgrade`, "Lock generation", owns the resolver procedure.
The resolver image ``kasvimuseo-resolver-issue087`` generated the production, development, and testing locks in that order.

Before the upgrade, the Django 5.2 image ``kasvimuseo-dev-issue087`` migrated ``issue088_upgrade``.
It then ran ``.dev/issue088/seed.py`` and dumped the application data to ``.dev/issue088/baseline-data.json``.
The runtime script uses ``--settings=ylaneenkasvit.test_settings`` for each management command.
It runs ``check``, ``makemigrations --check --dry-run kasvimuseo``, ``migrate --noinput``, ``migrate --check``, and ``showmigrations --plan``.
It compares the upgraded data with the baseline and migrates the separate ``issue088_fresh`` database.
It also checks static collection and the ``runserver_plus`` import.

Results
-------

This section records acceptance evidence from 2026-10-01 for reviewers.
Both images match their committed locks exactly and pass ``pip check``.
Neither image contains ExifRead, and the production image contains no ``django-extensions``.
The development image is ``427b73b73468``; the production image is ``95999168d2f1``.

The full application suite passes 538 tests.
The coverage run passes the coverage gate with 99.52% coverage.
System checks report no issues, and scoped migration generation reports no changes.
The database created under Django 5.2 has no pending migrations under Django 6.0.7.
Its application data remains byte-for-byte identical after the upgrade.
All migrations apply to an empty database, and ``migrate --check`` passes there.

Both images collect static assets, including the Finnish date-picker asset.
The production system and static checks run against the installed package without a source mount.
The development ``runserver_plus`` command imports successfully.

Chromium passes all 36 browser checks.
WebKit passes 29 checks and skips seven Chromium-only checks.

All 78 issue-register and commit-reference checks pass.
The register contains 88 issue files and 88 ranking entries.
Each issue appears under exactly one ranking heading and one generated queue heading.
Above the issue 087 branch, only issue 088 changes; it enters "Not in the queue".
Run ``python3 .dev/issue088/review_tracker.py`` to repeat this comparison.
The documentation build passes with warnings treated as errors and produces ``.dev/docs/html/index.html``.
The browser containers and the task's PostgreSQL cluster stop after the checks.

Integration boundary
--------------------

This section tells the maintainer what must happen before this branch merges.
This branch contains the unmerged issue 087 commits from ``feature/upgrade-to-django-5-530``.
Merge that branch into local ``master`` first, then rebase this branch onto ``master``.
The base checkout holds uncommitted copies of this issue file and its ranking entry.
The owner of those edits must commit or discard them before either merge.
