==============================================================================
Issue 064: Nothing fails when coverage drops
==============================================================================

:Status: Fixed
:Severity: Medium
:Area: process / tests
:Reported: 2026-08-03
:Source: Reading ``docs/test-coverage-plan.rst`` beside
    ``.github/workflows/tests.yml``. The plan's "Targets and definition of
    done" ends "There is no CI yet, so the gate is the dev script, not a build
    server. Adding CI is a natural follow-up once the suite needs a database."
    CI has existed since 018, and ``grep -n coverage .github/workflows/*.yml``
    returned nothing
:Evidence: The coverage run itself --
    ``dev/kasvimuseo app coverage`` on ``master`` at ``aa4c39a``: 449 tests,
    940 statements, 20 missed, 97.87 %, with the table written out in
    ``docs/test-coverage-plan.rst`` under "Where coverage stands". The gate was
    then shown to work in both directions: with three test modules moved out
    of the tree and the suite still passing, the same command reported 95.96 %
    and exited 2, and with them back it reports 97.87 % and exits 0. Both runs
    and the smaller ones behind the choice of three are in "Verification".
    The CI half is the ``Check the coverage floor`` step
    in ``.github/workflows/tests.yml``, which runs that one command; the
    workflow was checked with ``actionlint``, since this repository cannot push
    to GitHub
:Depends on: (none) -- one configuration file, one line of the workflow and a
    rewritten ``app coverage``. 018 had to exist first and does
:Blocks: (none)
:Related: 018 -- the CI this issue completes. That issue put the existing
    commands on a runner and deliberately did not invent new ones; this adds
    the one command it left out, in the same shape and for the same reason
    036 -- the upgrade programme this protects. Seventeen stages remain, each
    rewriting dependencies, settings and eventually the Python version, and the
    suite is the only thing that says whether any of them broke something. A
    stage that silently stops exercising a module is exactly the failure this
    gate is for, and Stage 10 -- the Python 2.7 to 3.7 flip -- is where it is
    most likely
    017 -- the browser suite, which measures none of this: it runs on the
    host's Python 3 against the running application, so no line of it appears
    in the figures here, and no coverage floor covers what it covers
    034 -- the vendored ``admin_list`` fork, 13 of the 20 missed statements,
    excluded from the plan's target and scheduled for deletion at Stage 5
:Decision: One floor on the **total**, at 97 %, written in a ``.coveragerc`` at the repository root, enforced by ``dev/kasvimuseo app coverage`` and run by CI as a second step of the existing ``pytest`` job. Four choices, each argued where a reader meets it rather than only here. **The floor is just under today's real number** (97.87 %), not at it and not far below it: at it, one defensive ``except`` branch nobody can trigger turns an unrelated pull request into a coverage negotiation; far below it -- the plan's own "≥ 80 % overall" -- gates nothing, since the suite could lose a sixth of its reach and stay green. The headroom is nine statements nominally and thirteen in practice, because coverage 4.5.4 compares the rounded percentage and 97 therefore means 96.5; that is measured in "Verification" and written down in ``.coveragerc``, since a floor whose real value is half a point from its stated one should not have to be rediscovered. **A total rather than per-file minimums**: twenty-one files is twenty-one numbers to maintain, coverage 4.5.4 has no per-file thresholds at all before 5.0, and the one file whose number genuinely differs is the one file nobody intends to change. **The vendored fork stays in the measurement**, although the plan excludes it from its *target*: a target asks somebody to raise a number and a floor only refuses a fall, so nothing here asks for the fork to be chased -- but dropping 139 statements out of the measurement to protect the total is the opposite of a gate, and 034 will remove the file at Stage 5, at which point the total rises rather than needing renegotiation. **A step, not a job**: the browser suite is a separate job so that a drag-and-drop regression and a model regression arrive as two different red lights, and that argument does not carry here, because this is the same suite run twice -- a red coverage step can only mean the passing tests reach less code, never an independent regression, and a second job would additionally pay 80 seconds to rebuild the image on a machine it does not share. The alternative of running *only* ``app coverage`` in CI was rejected for the same reason the two steps are ordered as they are: a plain failure should be reported by the plain suite in 35 seconds, not arrive dressed as a coverage failure.
:Resolution: 0d0a30a -- ``.coveragerc`` with the floor, the exclusions and the argument for each; ``dev/kasvimuseo app coverage`` reading it, and no longer reporting a table for a suite that failed; the ``Check the coverage floor`` step in ``.github/workflows/tests.yml``; and "Where coverage stands" in ``docs/test-coverage-plan.rst``, dated, beside the plan's historical ``Outcome`` table which is left as the record of that plan. No tests were added: the number is reported as it is.

Problem
=======

``docs/test-coverage-plan.rst`` took the suite from 30 % to 97 % across five
work packages, and ends its targets section with a sentence that stopped being
true when issue 018 landed:

    There is no CI yet, so the gate is the dev script, not a build server.
    Adding CI is a natural follow-up once the suite needs a database.

There is CI. ``.github/workflows/tests.yml`` runs ``dev/kasvimuseo app test``,
the browser suite in two engines and the documentation build. It has never run
``dev/kasvimuseo app coverage``::

    $ grep -n coverage .github/workflows/tests.yml
    $                                       # nothing, before this change

Nor did the command itself fail on anything. It ended::

    coverage run ... -m pytest -q $* >/dev/null;
    coverage report -m

-- a report, printed unconditionally, with no threshold. The ``;`` is worth its
own sentence: a suite that *failed* had its output thrown away and its coverage
table printed anyway, and the command exited 0. The one existing gate reported
a red suite as a green-looking table.

So the 97 % was a number in a document rather than a property of the
repository. Nothing in the tree could tell you it was still true, and nothing
anywhere would notice it falling.

Impact
======

Coverage that nobody measures decays in one direction. The specific exposure is
``docs/upgrade-plan.rst``: seventeen of its twenty stages remain, each rewriting
dependencies, settings and eventually the interpreter, and the suite is the only
evidence any of them produces that nothing broke. A stage that quietly stops
exercising a module -- a dependency swap that makes a test skip rather than
fail, an import that moves, Stage 10's Python 3 flip changing what runs at all
-- is invisible without a floor, and each of those looks exactly like success.

Nothing about this is hypothetical for the number itself: the plan's table said
97 % of 722 statements and the tree today has 940, because Stage 2, issues 002,
003, 055, 057, 058 and 059 all arrived after it was written. The document could
not have been wrong to say what it measured, and could not have stayed right.

What was measured
=================

On ``master`` at ``aa4c39a``, 2026-08-03, 449 tests, all passing: **940
statements, 20 missed, 97.87 %**. The full table is in
``docs/test-coverage-plan.rst`` under "Where coverage stands", which is dated
and is the place that number is maintained from now on; the plan's ``Outcome``
table stays as the record of the plan, with a note on each saying which is
which.

Of the 20 missed statements, 13 are in the vendored ``admin_list`` fork (issue
034, deliberately never chased), 5 in ``models.py`` and 2 in
``photo_matching.py``. Only seven, in other words, are code this repository
wrote and does not execute. One of the seven is worth naming here and is
deliberately **not** fixed in this change: ``PlantingPhoto.__unicode__``
returns ``u'%s: %s' % (self.planting, self.observation)`` and ``PlantingPhoto``
has no ``observation`` field, so it would raise ``AttributeError`` if anything
ever called it. Nothing does. Adding a test for it would have raised the
measured number in the same change that sets a floor from it, which is the one
thing a floor should never be set from.

Decision
========

Set out in full in the ``Decision`` field above; the reasoning lives in three
places on purpose, each where somebody meets the thing it explains:

* ``.coveragerc`` -- what is measured, what is left out and why 97.
* ``dev/kasvimuseo``, at the ``coverage`` case -- why it is a second command,
  why the suite is silent while it passes, and why a failed suite reports no
  table.
* ``.github/workflows/tests.yml``, at the new step -- why a step rather than a
  job, and what it costs.

The alternatives considered and rejected are in the ``Decision`` field: a floor
at today's number, a floor at the plan's 80 %, per-file minimums, omitting the
vendored fork, a separate CI job, and replacing ``app test`` in CI with
``app coverage`` rather than running both.

Verification
============

Today's number::

    $ dev/kasvimuseo app coverage
    TOTAL                                    940     20    98%       # 97.87 %
    $ echo $?
    0

The gate refusing a drop. Three test modules moved out of the tree, the suite
still green, and the floor doing the only thing it is for::

    $ mv kasvimuseo/tests/test_templatetags.py \
         kasvimuseo/tests/test_admin_changelist.py \
         kasvimuseo/tests/test_project_urls.py /tmp/       # deliberate
    $ dev/kasvimuseo app coverage
    TOTAL                                    940     38    96%       # 95.96 %
    $ echo $?
    2

    $ mv /tmp/test_templatetags.py /tmp/test_admin_changelist.py \
         /tmp/test_project_urls.py kasvimuseo/tests/       # and back
    $ dev/kasvimuseo app coverage
    TOTAL                                    940     20    98%
    $ echo $?
    0

None of it is committed. ``exit 2`` is coverage's own status for a failed
threshold, and a non-zero status is all a workflow step needs.

Three modules rather than one, because one is not enough, which is worth
recording as the honest measure of what this gate is: **this suite overlaps
heavily**. Removing ``test_templatetags.py`` alone costs six statements and
leaves 97.23 %; ``test_admin_changelist.py`` alone, six; ``test_project_urls.py``
alone, six. Each of those passes. The floor is therefore not a tripwire on any
one test file -- what it catches is a module dropping out of the suite
altogether, or new code arriving with none. That is the thing the upgrade
stages can do by accident, and it is what the floor is set for.

The other half of the old command, shown by accident while looking for a
regression big enough to cross the floor. With ``kasvimuseo/tests/test_models.py``
moved out, 71 tests fail and 45 error -- and the new command prints pytest's
output and exits 1, where the old one would have thrown that away and printed a
table::

    71 failed, 296 passed, 3 warnings, 45 error in 122.38 seconds
    $ echo $?
    1

One property of the installed coverage was measured rather than assumed, since
it changes what the floor means: **4.5.4 compares the rounded percentage**.
``coverage report --fail-under=98`` passes today at 97.87 %, and
``--fail-under=99`` fails. So ``fail_under = 97`` refuses anything below
96.5 %, half a point looser than it reads, and about thirteen statements below
today. There is no ``precision`` setting to tighten that with before coverage
5.0, which needs Python 3 and so arrives with upgrade Stage 10. It is written
down in ``.coveragerc`` beside the number rather than left to be rediscovered.

Cost::

    $ dev/kasvimuseo app test        # 35 s on a warm cluster
    $ dev/kasvimuseo app coverage    # 44 s

About a quarter longer, the tracer running on every line of every request. The
``pytest`` job therefore goes from roughly one minute to under two and remains
the fastest of the three; the browser jobs are two and a half minutes each and
run alongside, so the wall clock of a whole CI run is unchanged.

The rest of the suite is unaffected: ``dev/kasvimuseo app test``,
``dev/kasvimuseo app browser-test`` in Chromium and WebKit, and
``dev/kasvimuseo docs`` are all green, and ``actionlint`` passes on the
workflow.

What this does not do
=====================

* **It does not measure the browser suite.** ``browser_tests/`` runs on the
  host's Python 3 against the running application, so none of its work appears
  in these figures (issue 017). A drop there is caught by those tests failing,
  not by this floor.
* **It does not run in the pre-push hook.** ``dev/pre-push`` still runs
  ``app test`` alone, so a push costs 25 seconds rather than 45. The hook is a
  courtesy; the gate is CI, which cannot be skipped with ``--no-verify``.
* **It does not raise coverage.** No test is added here, deliberately. A floor
  set from a number the same change earned is a floor set from a number nobody
  has lived with.
