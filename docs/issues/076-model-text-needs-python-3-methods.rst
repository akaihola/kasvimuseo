Issue 076: Model text needs Python 3 methods
============================================

:Status: In progress
:Claimed: branch ``feature/plan-the-runtime-sta-sdz``
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-05
:Source: Backlog refill from upgrade plan Stage 10
:Evidence: ``requirements/production.txt`` pins Django 1.11.29; both images use Python 2.7.
:Depends on: (none)
:Blocks: 077 -- prepare model text before the interpreter transition
:Related: 036 -- the runtime upgrade programme
:Decision: Prepare the working model text methods for Stage 10 on the current runtime.
    The agent selected this reversible step under the autonomous task instruction.
    Keep the interpreter and package pins unchanged until the transition passes its own checks.
:Resolution: (none yet)

Work
----

This issue is for the implementation agent. It defines the next bounded runtime change.

Prepare the ten working model text methods and the report action for Python 3.
Keep the current runtime and pins.
See :doc:`../upgrade-plan`, Stage 10.
PlantingPhoto is outside this issue because its text method has a separate defect.
