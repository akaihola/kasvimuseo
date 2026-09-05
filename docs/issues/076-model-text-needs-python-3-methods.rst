Issue 076: Model text needs Python 3 methods
============================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-05
:Source: Backlog refill from upgrade plan Stage 10
:Evidence: ``requirements/production.txt`` pins Django 1.11.29; both images use Python 2.7.
:Depends on: (none)
:Blocks: 077 -- prepare model text before the interpreter transition
:Related: 036 -- the runtime upgrade programme
:Decision: Follow issue 036's Decision for this bounded source change.
:Resolution: The source preparation and checks are complete; the commit reference follows.

Work
----

This issue is for the implementation agent. It defines the next bounded runtime change.

See :doc:`../upgrade-plan`, Stage 10, Source preparation, for the change.
Issue :doc:`078-planting-photo-text-reads-a-missing-attribute` owns the excluded method.

Checks
------

The agent checked the change on 2026-09-05 with Python 2.7 and the existing Django pin.

* The development image built with the task-specific tag ``kasvimuseo-dev-036-sdz``.
* The baseline passed 528 tests after the backlog correction.
* The focused model and admin checks passed 76 tests.
* The full suite passed through ``dev/kasvimuseo app coverage`` with 99.40% coverage.
* Django's system check found no issues.
* The scoped migration check found no application changes.
* The documentation build passed with warnings treated as errors.

The existing report tests check Finnish skipped-species messages and identifier URLs.
The new conversion test checks UTF-8 output for all ten converted models.
The model tests also check Finnish names in nested labels.
Python 3 execution and deployment remain untested in this change.

The first baseline failed because the claims left the ready queue empty.
Filing the confirmed issue 078 restored a ready item; the next baseline passed.
The documentation builder needed a writable uv cache and network access for its dependencies.
