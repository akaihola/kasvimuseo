====================================================
Issue 018: No CI: the suite is only ever run by hand
====================================================

:Status: Open
:Severity: Medium
:Area: process
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: dev/kasvimuseo app test
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- a browser suite needs somewhere to run
    038 -- the documentation build moves into CI once one exists
    008 -- the kind of empty-database failure CI would catch
:Decision: undecided
:Resolution: (none yet)

Problem
=======

There is no continuous integration. The 245-test suite runs only when someone types
``dev/kasvimuseo app test``, so a regression is caught whenever a developer next happens
to run it, rather than on push.

The suite is well suited to CI: it needs PostgreSQL but no production dump and no media
download, and it finishes in about ten seconds.

Impact
======

Regressions can sit unnoticed. The coverage this work added is only as useful as the frequency with which it is run.

Options
=======

1. Add a pipeline that builds ``dev/Containerfile``, starts PostgreSQL and runs
   ``pytest``. The repository is on Bitbucket, so ``bitbucket-pipelines.yml`` is the
   native choice.
2. At minimum, a git pre-push hook running the suite locally.

Note the app is Python 2.7, so the CI image has to be the project's own container rather
than a current language runtime.
