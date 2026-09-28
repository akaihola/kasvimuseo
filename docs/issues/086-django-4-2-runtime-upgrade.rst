Issue 086: Django 4.2 is the next runtime upgrade step
======================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 17
:Evidence: Both images match their locks. The suite, browser checks, and migration checks pass; see "Checks".
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 17 through Django 4.0 and 4.1, then move to Django 4.2 on Python 3.12.
:Resolution: 4c6fd5a replaces removed APIs; 3fd066f upgrades the runtime and storage settings.

Work
----

This issue is for the implementation agent. It tracks Stage 17 of :doc:`../upgrade-plan`.

Move the project from Django 3.2 through Django 4.0.10 and 4.1.13 to Django
4.2.30 LTS after issue 085. Replace removed translation and text APIs, remove
``pytz``, update compatible dependencies, and move Python to 3.12. At Django
4.2, configure file and static storage through ``STORAGES``.

Compatibility changes
---------------------

This section explains the runtime changes for maintainers.
The implementation replaces removed translation, text, URL routing, and URL quoting APIs.
The orientation migration replaces ``NullBooleanField`` with a nullable ``BooleanField``.
It preserves null, true, and false values.
Historical migrations remain unchanged.

Grappelli 3.0.10 renders exactly the configured number of dashboard columns.
The dashboard now explicitly requests three columns so recent actions remain visible.
Werkzeug 0.8.3 fails on Python 3 because it calls ``dict.iteritems()``.
The development lock replaces it with Werkzeug 3.0.6.

``STORAGES`` explicitly selects the existing filesystem and static-file backends.
Both images use Python 3.12.12 on Alpine 3.22.
The dependency files own the final package versions.

Issue 085 already completed the prerequisite runtime upgrade.
The dependency field now names no unfinished prerequisite.
This removes an asymmetric dependency without editing issue 085.
Every other issue document must remain identical to local ``master``.

Checks
------

This section records the validation commands for reviewers.
Run these commands from the task checkout::

    export SHELL="$(command -v bash)"
    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue086-42
    export KASVIMUSEO_PG_PORT=5786
    export KASVIMUSEO_DB_NAME=issue086_upgrade
    dev/kasvimuseo app build
    podman build -t kasvimuseo-prod-issue086 -f Dockerfile .
    python3 .dev/issue086/check_packages.py
    dev/kasvimuseo app coverage
    dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --noinput --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage showmigrations --plan --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage shell --settings=ylaneenkasvit.test_settings -c 'import runpy; runpy.run_path(".dev/issue086/check_orientation.py")'
    KASVIMUSEO_DB_NAME=issue086_fresh dev/kasvimuseo app manage migrate --noinput --settings=ylaneenkasvit.test_settings
    KASVIMUSEO_DB_NAME=issue086_fresh dev/kasvimuseo app manage migrate --check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage shell --settings=ylaneenkasvit.test_settings -c 'import runpy; runpy.run_path(".dev/issue086/check_static.py")'
    podman run --rm -i -e DJANGO_SETTINGS_MODULE=ylaneenkasvit.test_settings kasvimuseo-prod-issue086 python < .dev/issue086/check_static.py
    dev/kasvimuseo app browser-test --engine chromium
    dev/kasvimuseo app browser-test --engine webkit
    dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py
    dev/kasvimuseo docs --clean
    git diff --check
    git diff master --name-only -- docs/issues/
    git status --short --untracked-files=all -- docs/issues/

Scripts, inventories, and logs live in ``.dev/issue086/`` in this task checkout.
The package audit checks exact versions, missing packages, unexpected packages, and ``pip check`` in both images.
It permits only identified packaging tools and the installed production application as extras.
The static check uses temporary output and checks the Finnish date-picker asset.
The production check runs without a source mount.

Lock generation
~~~~~~~~~~~~~~~

This section records the resolver environment for package maintainers.
The intermediate releases use the Python 3.10 resolver from issue 085, "Lock generation".
They use Django 4.0.10 with Photologue 3.15.1, then Django 4.1.13 with Photologue 3.16.
Both use Grappelli 3.0.10 and django-extensions 3.2.3.

The final resolver uses ``python:3.12.12-alpine3.22`` and the development image's build dependencies.
Both builders and the resolver use pip 24.0, setuptools 75.8.0, and wheel 0.45.1.
The resolver adds pip-tools 7.4.1 and Click 8.1.8.
Run the final resolution in that image::

    podman run --rm -v "$PWD:/src" -w /src kasvimuseo-resolver-issue086 sh -ec '
      pip-compile --resolver=backtracking --no-build-isolation \
        --no-emit-index-url --no-emit-trusted-host \
        -P asgiref==3.12.1 -P packaging==26.2 -P sqlparse==0.5.5 \
        --output-file=requirements/production.txt requirements/production.in
      for name in dev testing; do
        pip-compile --resolver=backtracking --no-build-isolation \
          --no-emit-index-url --no-emit-trusted-host \
          --output-file=requirements/$name.txt requirements/$name.in
      done'

Results
~~~~~~~

This section records completed checks on 2026-09-28 for reviewers.

* Django 4.0.10 passed 535 tests, system checks, and migration checks on Python 3.10.19.
* Django 4.1.13 passed the same 535 tests and checks on Python 3.10.19.
* Django 4.2.30 passed the full suite with 99.52% coverage, above the 97% gate.
* Both final images built and report Python 3.12.12 and Django 4.2.30.
* All 11 production packages and 19 development/test packages match their locks.
  Both images pass ``pip check`` and contain no ``pytz``.
* The development image contains the packaging tools listed under "Lock generation".
  The production image retains its base's pip 25.0.1 and adds the installed application.
* The final system check reports no issues.
  The scoped migration check reports no model changes.
* All 37 migrations apply to an empty database.
  The database created under Django 3.2 also reaches the final migration state.
  Null, true, and false orientation values survive each intermediate upgrade.
* Both images collect static assets successfully with temporary storage settings.
  The production image passes its installed-application system check.
* Werkzeug and ``runserver_plus`` import successfully with the final development runtime.

The initial documentation build reached Sphinx and found the asymmetric dependency described under "Compatibility changes".
The build passed after that correction and produced ``.dev/docs/html/index.html``.
The heartbeat's output-lock and DNS failures did not recur in this checkout.

The development image is ``1d8c724c4e2a``; the production image is ``2779361aa30d``.
Chromium passed all 35 browser checks.
WebKit passed 28 checks and skipped seven Chromium-only checks.
All 78 issue-register and commit-reference tests pass after the final metadata changes.
The final documentation build passes with warnings treated as errors.
Only issue 086 moves in the tracker, from Open to Fixed.
Every other issue file matches local ``master`` exactly.

Deployment boundary
-------------------

This section identifies work outside the runtime acceptance checks for the deployment operator.
Issue 085, "Deployment prerequisite", records the older staging operating system and interpreter.
The operator must prepare a compatible target before deploying this runtime.
These local checks do not establish a live deployment.
