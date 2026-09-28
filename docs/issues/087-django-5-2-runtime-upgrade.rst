Issue 087: Django 5.2 is the next runtime upgrade step
======================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 18
:Evidence: Both images match their locks. Application, browser, system, and migration checks pass; see "Results".
:Depends on: 086
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Upgrade directly to Django 5.2.16 on Python 3.12 and replace GET logout with a protected POST form.
:Resolution: f4378cd replaces GET logout; 31b3ce8 upgrades the runtime and package locks.

Work
----

This issue tracks Stage 18 of :doc:`../upgrade-plan`.

Move the project from Django 4.2 to Django 5.2.16 LTS after issue 086. Keep
Python 3.12. Update ``django-grappelli`` to 4.0.4 and ``django-photologue``
to 3.19. Keep ``django-sortedm2m`` at 4.0.0 and ``pytest-django`` at 4.11.1.
Update the resolved package locks. Remove ``DEFAULT_FILE_STORAGE``,
``STATICFILES_STORAGE`` and ``index_together`` because Django 5.1 removes them.

Checks
------

Build both images. Confirm that their installed packages match the committed
locks. Run the application tests, browser tests, Django system check, migration
checks and documentation build. Record the commands and results here.

Implementation
--------------

This section explains the upgrade for maintainers.
The dependency inputs and resolved locks select the requested runtime versions.
The test dependency moves from pytest-django 4.8.0 to 4.11.1.
Both container definitions retain Python 3.12.12.

The logout control submits POST with a token that protects against cross-site request forgery.
A GET request leaves the session intact and returns HTTP 405.
Requests without the required token return HTTP 403.
The browser check submits the control from a species report and checks that administration requires another login.

The source already uses ``STORAGES``.
The source contains no ``DEFAULT_FILE_STORAGE``, ``STATICFILES_STORAGE``, or ``index_together`` usages.
The upgrade requires no model or migration edits.

The requested ``/move-doc`` command has no compatible implementation in this checkout.
The available external script moves Markdown files and commits in its own repository.
The agent used the repository's status field in place and retained this issue's path.

Validation commands
-------------------

This section gives reviewers the environment and commands for the acceptance checks.
Run them from the task checkout::

    export SHELL="$(command -v bash)"
    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue087
    export KASVIMUSEO_DB_NAME=issue087_upgrade
    export KASVIMUSEO_PG_PORT=5787
    export KASVIMUSEO_BROWSER_DB_NAME=issue087_browsertest
    dev/kasvimuseo app build
    podman build -f Dockerfile -t kasvimuseo-prod-issue087 .
    python3 .dev/issue087/check_packages.py
    dev/kasvimuseo app coverage
    bash .dev/issue087/check_runtime.sh
    podman run --rm -i -e DJANGO_SETTINGS_MODULE=ylaneenkasvit.test_settings \
      kasvimuseo-prod-issue087 python < .dev/issue087/check_static.py
    dev/kasvimuseo app browser-test --engine chromium
    dev/kasvimuseo app browser-test --engine chromium -k report_logout
    dev/kasvimuseo app browser-test --engine webkit
    dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py
    dev/kasvimuseo docs --clean
    git diff --check
    git diff master --name-only -- docs/issues/

Scripts, logs, and package inventories remain under ``.dev/issue087/`` in this task checkout.
:doc:`086-django-4-2-runtime-upgrade`, "Lock generation", owns the resolver procedure.
The same resolver generated production, development, and testing locks in that order, using ``kasvimuseo-resolver-issue087``.

The runtime script uses ``--settings=ylaneenkasvit.test_settings`` for each management command.
It runs ``check``, ``makemigrations --check --dry-run kasvimuseo``, ``migrate --noinput``, ``migrate --check``, and ``showmigrations --plan``.
It also applies migrations to the separate ``issue087_fresh`` database and checks static collection.
The tests leave the development media link unchanged.

Results
-------

This section records acceptance evidence for reviewers.
Both images match their committed locks exactly and pass ``pip check``.
The development audit also accounts for pip, setuptools, and wheel.
The production audit accounts for pip and the installed application.
The development image is ``d832df09701e``; the production image is ``3e3d82a1c23f``.

All 121 focused compatibility tests pass.
The full application suite passes the coverage gate with 99.52% coverage.
System checks report no issues, and scoped migration generation reports no changes.
All 37 migrations apply to an empty database.
The database created under Django 4.2 has no pending migrations under Django 5.2.
Its application data remains byte-for-byte identical after the upgrade.
The comparison includes three species with null, false, and true photo orientations and their planting histories.

Both images collect static assets, including the Finnish date-picker asset.
The production system and static checks run against the installed package without a source mount.
The development ``runserver_plus`` command imports successfully.

Chromium passes all 35 existing checks and the corrected logout check in a focused rerun.
The initial logout check targeted the compact report, which replaces the shared header.
The corrected check uses the species list, which displays the logout control.
WebKit passes 29 checks and skips seven Chromium-only checks.

All 78 issue-register and commit-reference checks pass after the final metadata changes.
The documentation build passes with warnings treated as errors and produces ``.dev/docs/html/index.html``.
Every other tracker file matches local ``master`` exactly.
The browser containers and the task's PostgreSQL cluster stop after the checks.

Deployment boundary
-------------------

This section identifies the remaining deployment work for the operator.
The private deployment repository owns the staging host check.
The operator must prepare a compatible host before deployment.
These checks establish local runtime compatibility.

Review checks
-------------

This section records the implementation review for maintainers.
The review found no implementation defect.
All 199 focused application and tracker checks pass.
The logout browser check passes in Chromium and WebKit.
Both package audits, system checks, migration checks, and the installed-production static check pass again.
The production logout template matches the committed source byte-for-byte.

The register contains 87 issue files and 87 ranking entries across nine headings.
Each issue appears under exactly one ranking heading and one generated queue heading.
The rendered queue contains one ready issue and 86 parked issues, with no duplicates or overlap.
Only issue 087 moves from "Ready now" to "Not in the queue" against local ``master``.
Every other tracker file matches ``master`` exactly.
The branch contains no merge commits above ``master``.

Run ``python3 .dev/issue087/review_tracker.py`` to repeat the tracker comparison.
The check stores each issue's heading in ``.dev/issue087/review-tracker.json``.
Review logs use the ``review-`` prefix under ``.dev/issue087/``.

Manual checks
-------------

This checklist is for testers of an instance running the upgraded release.

1. Sign in to the administration site.
2. Open the planted-species list and select its logout button.
3. Check that the page confirms logout.
4. Open the administration site and check that it requests another login.
5. Sign in again and check that you can upload photos, open reports, and edit planting labels.
