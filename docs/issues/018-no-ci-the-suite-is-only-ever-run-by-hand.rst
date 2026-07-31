====================================================
Issue 018: No CI: the suite is only ever run by hand
====================================================

:Status: Fixed
:Severity: Medium
:Area: process
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: dev/kasvimuseo app test
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- a browser suite needs somewhere to run, and now has one: the
    workflow this issue adds is where a headless browser job would be a third
    job, on the same image and the same cluster. 017's own status is unchanged;
    what it inherits is the runner, not the suite.
    038 -- the documentation build moves into CI once one exists, and has: the
    ``sphinx`` job runs ``dev/kasvimuseo docs``. 038 is still in progress and
    still owns the design of that build; this issue only put the existing
    command on a runner.
    008 -- the kind of empty-database failure CI would catch
:Decision: **GitHub Actions**, in ``.github/workflows/tests.yml``, plus the
    tracked ``dev/pre-push`` hook -- taken as the default when the ruling was
    asked for and skipped, and cheap to change. Both jobs have since passed on
    a hosted runner. See "Decision" below for what was asked and what each
    platform costs, and "It has run" for what the runner actually did.
:Resolution: Fixed in 331fd74.

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

Decision
========

Option 1 **and** option 2: a service pipeline plus the local hook.

The platform, which is the part option 1 left open
--------------------------------------------------

The sentence above -- "the repository is on Bitbucket, so
``bitbucket-pipelines.yml`` is the native choice" -- was true when it was
written and is no longer the whole picture. The checkout has two remotes:

======================= ============================================ ===========
Remote                  URL                                          State
======================= ============================================ ===========
``bitbucket``           ``bitbucket.org/akaihola/kasvimuseo``        what ``master`` tracks
``origin``              ``github.com/akaihola/kasvimuseo``           behind
======================= ============================================ ===========

So the choice was a real one, and not the agent's to make: nothing in the
repository says whether Bitbucket Pipelines is switched on for that account,
whether it has build minutes left, or whether the GitHub mirror is meant to
become primary. It was put to the maintainer -- Bitbucket Pipelines, GitHub
Actions, both, or the hook alone -- and skipped rather than answered, so what
is committed is the recommendation, and this section is what it rests on so it
can be overturned cheaply.

**GitHub Actions**, because a ``bitbucket-pipelines.yml`` is only worth having
if Pipelines is enabled and funded, and a committed pipeline that never runs is
worse than none: it reads, in a diff and to the next person, as coverage that
does not exist. GitHub Actions has no enabling step -- the file's presence is
the enablement -- and ``ubuntu-latest`` already ships podman and a PostgreSQL
server, so the workflow calls ``dev/kasvimuseo`` rather than paraphrasing it.

The cost of that choice was stated plainly rather than hidden: **the mirror was
behind, so nothing would run until it was pushed to.** That has since happened
-- see "It has run" below -- but it remains the standing condition of this
choice, not a one-off: work pushed only to ``bitbucket`` is tested by nothing
but the hook. If the answer is really Bitbucket, the same two commands go into
a ``bitbucket-pipelines.yml`` with a ``docker`` service and the same two runner
fixups; the work in this issue is the shape, not the YAML dialect.

The hook is the half that depends on none of that. It needs no account, no
build minutes and no network, and it is the only protection that exists while
the mirror is behind -- which is precisely the situation this issue is being
fixed in.

A cluster on the runner, not a service container
------------------------------------------------

The usual CI shape is a PostgreSQL service container reached over TCP. That
does not fit here without changing settings: ``common_settings.py`` gives the
database ``'HOST': '/var/run/postgresql'``, a unix socket *directory*, and
``test_settings`` does not override it. A service container would therefore
have needed a new ``KASVIMUSEO_DB_HOST`` override in the settings -- a change
in a file that issues 016, 023 and 024 are in flight in, made only to suit CI.

The arrangement ``dev/kasvimuseo`` already uses needs no such change: it
initialises a throwaway cluster under ``.dev/``, listens on a unix socket
inside the working copy, and bind-mounts that directory to
``/var/run/postgresql`` in the container. So the workflow starts nothing
itself; it runs the two commands a developer runs, and the settings are the
settings that already exist.

Two runner fixups, and why they are in the workflow
---------------------------------------------------

``dev/kasvimuseo`` assumes a developer machine in two small ways that a hosted
runner does not satisfy. Ubuntu installs PostgreSQL's server binaries under
``/usr/lib/postgresql/<version>/bin`` and puts only the client on ``PATH``, so
``initdb`` and ``pg_ctl`` are not found; and a non-login shell leaves ``$USER``
unset, which the script reads under ``set -u``. Both are properties of the
runner rather than defects in the script, so the workflow fixes them in a
``Prepare the runner`` step instead of the script growing fallbacks for a
machine it will never otherwise meet.

The documentation build, which is 038's and is here anyway
-----------------------------------------------------------

038's ``:Related:`` says the docs build moves into CI once one exists. 038 is
in progress under another workstream, so nothing of its was touched -- not its
file, not ``dev/docs-build``, not ``docs/``. What was added is one job that
runs the command 038 already provides.

It earns its place rather than merely being available: warnings are errors, and
``docs/issues/next.rst`` is generated from these files' own metadata, so the
job fails on a malformed ``:Status:``, an issue missing from the ranking, or a
broken reference -- the one class of mistake in this register that is otherwise
found by whoever next builds the docs, which may be days later. It shares
nothing with the test job (host Python 3 through ``uv``, no container, no
database), so it runs in parallel and adds no wall-clock time.

What it costs
=============

Measured on a four-core development machine, and then on the runner itself once
the pull request existed:

========================================== =============== ===============
Step                                       Here            GitHub runner
========================================== =============== ===============
``app build``, no cache, base image pulled 1 min 20 s      included below
``app test``, the whole suite              25 s            1 min 6 s
``docs``, clean, in the parallel job       20 s            28 s
**A full run**, the two jobs at once       **about 2 min** **about 1 min**
========================================== =============== ===============

The runner's ``pytest`` figure is the whole job -- checkout, image build and
suite together -- so the image costs less on a hosted two-core runner than the
arithmetic here suggests, and the two jobs run at the same time. Locally the
tests are 19 to 22 seconds of that 25 and the rest is initialising, starting
and stopping the cluster; most of the build is compiling Pillow and psycopg2
against musl. Caching the image on its build inputs would take a chunk off each
run and was left out deliberately: it is machinery to maintain, and a
one-minute pipeline is not what anybody is waiting for.

The suite needs no production dump and no ``media fetch``. That was checked
rather than assumed: ``test_settings`` sets ``MEDIA_ROOT`` to a throwaway
directory, and the whole suite passes in a container with no ``media/``
mounted -- on the runner too, which has neither and could fetch neither. No
test turned out to need media, and no test was changed, skipped or weakened
for CI.

The 245 in "Problem" above is the count when this was filed. It was 402 while
this was being written, and it moved twice during the writing, as 016, 024 and
045 landed on ``master``. The growth rather than the number is this issue's
point, which is why the table above counts seconds and not tests.

It has run
==========

The first real run could not be triggered from the branch -- it needs a push to
a remote this working copy has no credentials for -- so everything the workflow
does was run locally first, in the workflow's own order. The maintainer then
opened `pull request 1 <https://github.com/akaihola/kasvimuseo/pull/1>`_, and
both jobs passed on a hosted runner at the first attempt: ``pytest`` green in
1 min 6 s, ``sphinx`` in 28 s. The two assumptions this fix rests on are
therefore facts rather than expectations -- ``ubuntu-latest`` does carry podman
and a PostgreSQL server, and rootless podman does start this image and reach
the cluster's socket through the bind mount.

That run also found the one defect in the first version of the workflow, and
found it the way CI is supposed to: the maintainer saw it before anybody
explained it. Every job ran twice, because a bare ``push:`` alongside
``pull_request:`` matches both events for a branch with a pull request open.
The push trigger is now limited to ``master``, so a pull request builds its
merge commit while it is open and ``master`` builds what lands. The gap that
leaves -- a branch pushed with no pull request open runs nothing -- is exactly
what ``dev/pre-push`` covers, which is part of why both halves are here.

What is left is small:

1. Install the hook in each clone. It is one line, in ``README.rst`` under
   "Continuous integration".
2. Decide whether pushing to GitHub is part of the routine now, since that is
   the remote the workflow watches, or whether this should move to Bitbucket
   after all. If it moves, the same two commands go into a
   ``bitbucket-pipelines.yml`` with the same two runner fixups; nothing else in
   this fix depends on which service runs them.
3. If ``pytest`` ever fails on the runner and not locally, read it as a
   PostgreSQL version difference before anything else: the runner's server
   version is the one thing CI has that a developer machine does not.
