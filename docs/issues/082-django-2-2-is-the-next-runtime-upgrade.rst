Issue 082: Django 2.2 is the next runtime upgrade step
======================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 13
:Evidence: Both runtimes pass 531 tests. The images match their locks; browser, migration and documentation checks pass.
:Depends on: (none)
:Blocks: 083
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 13 with separate Django and Python commits. Use Debian 11 for the matching deployment interpreter.
:Resolution: 41e207e upgrades Django; 8a97f5f upgrades Python; dc78466 repairs the browser checks; 3bc707f guards web-only deployments.

Work
----

This issue is for the implementation agent. It tracks Stage 13 of :doc:`../upgrade-plan`.

Update the runtime to Django 2.2.28, Grappelli 2.13.4, Photologue 3.10,
sortedm2m 2.0.0 and a compatible pytest-django release. Move Python from 3.7
to 3.9 in a separate commit from the Django upgrade. Keep the package locks in
step with the pins.

Checks
------

This section records the commands and results for reviewers.

Run these commands from the task checkout::

    export SHELL="$(command -v bash)"
    export KASVIMUSEO_IMAGE=kasvimuseo-dev-issue082
    export KASVIMUSEO_PG_PORT=5782
    export KASVIMUSEO_DB_NAME=issue082
    dev/kasvimuseo app build
    podman build -t kasvimuseo-prod-issue082 -f Dockerfile .
    podman run --rm kasvimuseo-dev-issue082 pip check
    podman run --rm kasvimuseo-prod-issue082 pip check
    podman run --rm kasvimuseo-dev-issue082 pip list --format=json
    podman run --rm kasvimuseo-prod-issue082 pip list --format=json
    dev/kasvimuseo app test
    dev/kasvimuseo app coverage
    dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage migrate --noinput --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app manage showmigrations --plan --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo app browser-test --engine chromium
    dev/kasvimuseo app browser-test --engine webkit
    dev/kasvimuseo docs --clean

The checks use this checkout's PostgreSQL directory and test media.
They do not use another checkout's database or production data.

Results on 2026-09-27:

* Django 2.2.28 on Python 3.7.17 passed all 531 tests with 99.52% coverage.
  Both images built and matched their locks: 15 production packages and 25 development packages.
* Django 2.2.28 on Python 3.9.25 passed all 531 tests with 99.53% coverage.
  Both images built and matched their locks: 12 production packages and 22 development packages.
* Both runtime boundaries passed ``pip check``, Django's system check and the scoped migration check.
  All 33 migrations applied, with none pending.
* Both documentation builds passed with warnings treated as errors.
  Each build produced ``.dev/docs/html/index.html``.

The test warnings concern Pillow's ``ANTIALIAS``, Django 3.1's ordering change, and Photologue sampling a set on Python 3.9.
The later upgrade stages own those compatibility changes.

Lock generation
~~~~~~~~~~~~~~~

Issue 077, "Checks", owns the lock generation command and its order.
The Django commit ran it under Python 3.7 with pip-tools 6.14.0.
The Python commit ran it inside ``python:3.9.25-alpine3.22`` with the image's packaging tools and pip-tools 6.14.0.
That resolver container installed ``gcc``, ``musl-dev``, ``postgresql-dev``, ``jpeg-dev`` and ``zlib-dev`` before resolution.

sortedm2m 2.0.0 adds ``six`` to the production lock.
The duplicate development pin conflicted with that lock and was removed.
Python 3.9 removes the unused ``importlib-metadata``, ``typing-extensions`` and ``zipp`` compatibility packages.
The other compatible pins remain unchanged.

Browser checks
~~~~~~~~~~~~~~

Chromium passed all 35 tests.
WebKit passed 28 tests and skipped seven Chromium-only touch checks.

The browser run exposed stale test support that prevented the checks from passing.
The seed script now initializes Django before model imports and uses ``user_permissions.set()``.
The admin test uses Grappelli's submit button to run the selected action.
The label measurement now returns the CSS position that its assertion reads.

The validation logs and image identifiers live in ``.dev/issue082/`` in the task checkout.

Deployment prerequisite
-----------------------

This section tells deployment operators which host can run this revision.

Prepare a Debian 11 target before deployment.
Its ``uwsgi-plugin-python3`` package depends on ``libpython3.9``.
The deployment checks the distribution before it changes the application environment.
It rejects Debian 10, Debian 12 and other distributions.

The staging inventory still describes Debian 10 with Python 3.7.
The deployment operator owns its transition to a matching target.
This issue changes the repository runtime and does not deploy or upgrade a server.

Local deployment checks
~~~~~~~~~~~~~~~~~~~~~~~

The Debian 11 package check found Python 3.9.2 and uWSGI 2.0.19.1.
The uWSGI plugin declares its ``libpython3.9`` dependency in package metadata.

Run the syntax check with the environment described in
``.agents/memory/running-ansible-from-this-checkout.md``::

    uvx --from ansible ansible-playbook -i 'localhost,' --syntax-check ansible/install.yaml

The syntax check passed with existing NGINX role deprecation warnings.
A temporary local play exercised the deployment assertion with four distribution cases.
Debian 11 passed; Debian 10, Debian 12 and Ubuntu 22 failed before mutations.
The play ended with four successful checks, three expected rejections and no failed checks.

Review checks
-------------

This section records the implementation review for maintainers.

Check the web deployment tasks with the same local Ansible environment::

    uvx --from ansible ansible-playbook -i 'localhost,' ansible/install.yaml --list-tasks --tags web

The review found that ``--tags web`` selected uWSGI but skipped the runtime guard.
The guard now carries that tag and runs before uWSGI installation.
Local checks accept Debian 11 and reject Debian 10 under each application tag: ``python``, ``code``, ``static``, ``web`` and ``uwsgi``.

All 164 focused tracker, commit-reference, admin, photo and routing tests passed.
Both images still match their locks and pass ``pip check``.
The register contains 84 issue files and 84 unique ranking entries across all headings.
Its generated queue contains two ready issues and 82 parked issues, with no overlap.
Only this issue differs from ``master`` in ``docs/issues/``.

The focused browser checks passed four cases in Chromium and three in WebKit.
WebKit skipped one Chromium-only touch case.
