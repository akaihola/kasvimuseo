Issue 077: The Python 3 runtime needs a rehearsed transition
============================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-05
:Source: Backlog refill from upgrade plan Stage 10
:Evidence: 531 Python 3 tests pass; both images build; the isolated Ansible deployment, backup restoration, rollback, and redeployment pass.
:Depends on: 076, 078 -- finish model text before the interpreter transition
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 10 with the compatible Python 3.7 runtime and an isolated rehearsal. Keep the later upgrades in issue 036.
:Resolution: 51fe8ba changes the runtime; c32c664 repairs archive assets; ce3bc43 changes and rehearses Ansible; 5a9c76f repairs code-only updates.

Checks
------

This issue is for runtime maintainers. It records the transition checks and the evidence for closing Stage 10.

Run these commands from the repository root::

    KASVIMUSEO_IMAGE=kasvimuseo-077-dev dev/kasvimuseo app build
    podman build -t kasvimuseo-077-prod -f Dockerfile .
    KASVIMUSEO_IMAGE=kasvimuseo-077-dev KASVIMUSEO_PG_PORT=5577 KASVIMUSEO_DB_NAME=issue077 dev/kasvimuseo app test
    dev/kasvimuseo docs

Regenerate the locks inside the development image::

    podman run --rm -v "$PWD:/src" -w /src kasvimuseo-077-dev sh -ec '
      pip install pip-tools==6.14.0
      for name in production dev testing; do
        pip-compile --resolver=backtracking --no-build-isolation \
          --no-emit-index-url --no-emit-trusted-host \
          --output-file=requirements/$name.txt requirements/$name.in
      done'

Use ``README.rst``, "Running it", for the Ansible source and seed parameters.
Keep the database and media isolated from other worktrees.

Support checks
--------------

The implementation checked the following official sources on 2026-09-14 before selecting versions:

* `Django 1.11.17 release notes <https://docs.djangoproject.com/en/4.2/releases/1.11.17/>`_ establish Python 3.7 compatibility.
* `Python's release schedule <https://peps.python.org/pep-0537/>`_ records Python 3.7's end of support.
* `Pillow's Python support table <https://pillow.readthedocs.io/en/stable/installation/python-support.html>`_ includes Python 3.7 for Pillow 9.5.
* `Gunicorn 21.2.0 metadata <https://pypi.org/project/gunicorn/21.2.0/>`_ defines its Python requirements.
* `psycopg2 2.8.6 metadata <https://pypi.org/project/psycopg2/2.8.6/>`_ includes Python 3.7 builds.
* `The driver's Django compatibility report <https://github.com/psycopg/psycopg2/issues/1293>`_ supports retaining the documented ceiling below 2.9.
* `ExifRead 2.1.2 metadata <https://pypi.org/project/ExifRead/2.1.2/>`_ lists Python 3 support.
* `pip-tools 6.14.0 metadata <https://pypi.org/project/pip-tools/6.14.0/>`_ permits resolving with Python 3.7.

The old production lock actually installed psycopg2-binary 2.8.4.
Stage 10's claim that it already used 2.8.6 was incorrect.
The generated lock now matches the chosen Stage 10 driver.
See :doc:`../upgrade-plan`, "Interpreter transition", for the other version decisions.

The host resolver failed while building sortedm2m with modern setuptools.
The container resolver succeeded with pip 23.1.2, setuptools 57.5.0, and wheel 0.41.3.
Both image builders and Ansible use that toolchain.

Rehearsal evidence
------------------

The rehearsal ran on gogo on 2026-09-14.
The recorded remote staging host timed out on SSH.
An isolated Debian 10 container supplied systemd, PostgreSQL 11, NGINX, and both uWSGI interpreter plugins instead.
Its web endpoint listened only on the container's loopback interface.
No production service or shared database changed.

The starting code came from 2c7d43c.
The development baseline reported Python 2.7.18 and passed all 530 existing tests.
The deployed baseline reported Python 2.7.16, Django 1.11.29, and the original production pins.
The original production build failed because its install option forced Photologue's broken source build.
Using ``--prefix`` allowed its wheel and produced the preserved Python 2 image.

The seed came from the existing ``production-migrated.sql`` dump.
The worktree's private database applied the remaining migrations before the runtime transition.
The PostgreSQL 11 seed copy omitted newer dump settings and client guard commands.
The application data required no conversion.

The deployment checks recorded 156 species, 311 observations, 137 photos, and 28 applied migrations.
The media backup held 403 files after the baseline rendered its pages.
The checks covered login, admin lists, labels, label data, Finnish text, photo bytes, and timezone queries.
Authenticated HTTP requests passed through NGINX and uWSGI, as well as Django's test client.

#. The agent recorded the baseline and backed up the database, media, service configuration, and package inventory.
#. Ansible installed the candidate archive into the separate Python 3.7 environment.
#. The agent checked the deployed pages, data counts, migrations, media checksums, and package versions.
#. The agent added a database table and media file to test restoration.
#. The agent restored both backups and the previous uWSGI configuration.
#. The rollback checks found both probes absent and all original media checksums intact.
#. The restored Python 2 service passed the same data and HTTP checks.
#. Ansible redeployed Python 3 and repeated the play without a database seed.
#. Both runs passed the same checks again.

The Debian target reported Python 3.7.3; the images reported Python 3.7.17.
The repeat play completed with ``ok=16 changed=4 failed=0``.
The changes were application installation, executable permissions, static collection, and service restart.
The runtime bootstrap and uWSGI configuration required no changes on that repeat.

Both images passed ``pip check`` and matched their applicable locks.
Django's deployed management check reported no issues.
The audit helper and the password helper's empty dry run executed under Python 3.
The new media test checked a Unicode filename, an existing file, and a failed HTTP request.
The full Python 3 suite passed 531 tests with 1,211 dependency warnings.

The archive check found and repaired missing report templates and vendored assets.
All 27 template and static files matched their source bytes in the corrected archive.
Both production image commands and Gunicorn returned HTTP 200 against the restored database.
The documentation build wrote its HTML index.

The task worktree retains logs and backups under ``.dev/rehearsal/``.
The principal logs are ``python3-tests.log``, ``image-smoke.log``, ``deploy3.log``, ``rollback.log``, and ``repeated-checks.log``.
The candidate archive's SHA-256 is ``61f1d13eb619d2c9535bfff49b1f651d0d8d00af5c63e21e44c26c8df917090f``.
The database backup's SHA-256 is ``84ccc446d08797445bb618df944c51b0a03e10503dd2fd44038a02bc85f94d35``.
The media backup's SHA-256 is ``225560e53544829557e7bbcff40b8672286f527aa4264552934803d94ba67e49``.

Review checks
-------------

The review found that ``--tags code`` omitted the uWSGI role and its restart condition.
The corrected code-only deployment passed with Ansible using Python 2.7 and the application using Python 3.7.
The service timestamp changed, and the data, media, and HTTP checks passed again.
The log is ``.dev/rehearsal/review-code.log``.

The focused regression suite passed 204 tests.
Both images still matched the runtime lock, and the stored backup hashes matched the recorded evidence.
The register parser and both rendered tables contained 78 issues, each under exactly one heading per page.
Only this issue file differs from ``master`` in the issue tracker.

What remains
------------

Issue 036 owns the later runtime upgrades.
The maintainer owns any live deployment and its measurements before deployment.
A live deployment requires separate execution.
