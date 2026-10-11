=========================================================
Issue 036: The runtime stack is end-of-life and unpatched
=========================================================

:Status: Fixed
:Severity: High
:Area: platform / security
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: See :doc:`076-model-text-needs-python-3-methods`, Checks.
:Depends on: 016, 019, 020, 021, 022, 023, 024, 027, 028, 029, 030, 031, 033, 034 -- the individual obstacles, listed in the upgrade plan
:Blocks: (none)
:Related: 035 -- the ceiling that will make this recur
    040 -- option 3 there is to wait for this
    038 -- most of the documentation build's workarounds fall away at Stage 10
    018 -- CI has to run the project's own container until Stage 10
:Decision: The programme ends with the source upgrade, not with a deployment.
    Stage 19 landed Django 6.0.7 on ``main`` as the last stage.
    The private deployment repository owns the host work for the new runtime, so this public record cannot track it.
:Resolution: 8bd0599 merges Stage 19 into ``main``; bcff77c is the upgrade commit.
    See :doc:`088-django-6-0-runtime-upgrade`, "Results".
    Every stage in :doc:`../upgrade-plan`, Part 4, reads ``Done``.

Work
----

This issue recorded the runtime upgrade programme.
Read :doc:`../upgrade-plan`, "Part 4 — The upgrade sequence", for the stages and the commits that landed them.
The private deployment repository owns the original installation measurements and migration rehearsals.
