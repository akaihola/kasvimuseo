=========================================================
Issue 036: The runtime stack is end-of-life and unpatched
=========================================================

:Status: Accepted
:Severity: High
:Area: platform / security
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: See :doc:`076-model-text-needs-python-3-methods`, Checks.
:Depends on: 016, 019, 020, 021, 022, 023, 024, 027, 028, 029, 030, 031, 032, 033, 034 -- the individual obstacles, listed in the upgrade plan
:Blocks: (none)
:Related: 035 -- the ceiling that will make this recur
    040 -- option 3 there is to wait for this
    038 -- most of the documentation build's workarounds fall away at Stage 10
    018 -- CI has to run the project's own container until Stage 10
:Decision: Prepare the working model text methods for Stage 10 on the current runtime.
    The agent selected this reversible step under the autonomous task instruction.
    Keep the interpreter and package pins unchanged until the transition passes its own checks.
:Resolution: 72b1a99 completes the bounded source preparation.
    See :doc:`076-model-text-needs-python-3-methods`, Checks.
    The interpreter transition remains in issue 077.

Work
----

This issue guides maintainers through the runtime upgrade programme.
Read :doc:`../upgrade-plan`, "Part 4 — The upgrade sequence", for the stages and their status.
The private deployment repository owns the original installation measurements and migration rehearsals.
