Issue 077: The Python 3 runtime needs a rehearsed transition
============================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-05
:Source: Backlog refill from upgrade plan Stage 10
:Evidence: 531 Python 3 tests pass, and both images build.
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

The private deployment repository owns the source and seed parameters.
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
Both image builders use that toolchain.

Review checks
-------------

The review found that ``--tags code`` omitted the uWSGI role and its restart condition.
The private deployment repository owns the deployment check results.
The service timestamp changed, and the data, media, and HTTP checks passed again.
The log is ``.dev/rehearsal/review-code.log``.

The focused regression suite passed 204 tests.
Both images still matched the runtime lock, and the stored backup hashes matched the recorded evidence.
The register parser and both rendered tables contained 78 issues, each under exactly one heading per page.
Only this issue file differs from ``master`` in the issue tracker.

Deployment records
------------------

The private deployment repository owns rehearsal evidence and operations follow-up.
