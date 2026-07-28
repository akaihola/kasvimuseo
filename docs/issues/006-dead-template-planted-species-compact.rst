======================================================
Issue 006: Dead template: planted-species-compact.html
======================================================

:Status: Open
:Severity: Low
:Area: templates / cleanup
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py (covers the live path instead)
:Depends on: (none)
:Blocks: (none)
:Related: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``reports/planted-species-compact.html`` is 165 lines and nothing references it. A grep
across ``.py`` and ``.html`` finds no user. ``PlantedSpeciesCompact`` renders
``reports/planted-species.html`` with ``planted-species-base-compact.html`` as its base.

It is also internally inconsistent: it mixes top-level ``{{ species.* }}`` with
``{{ page.beds }}``, so if it were ever wired up the names and photo would render empty.

Impact
======

165 lines that look load-bearing but are not, and would misbehave if used.

Options
=======

1. Delete it.
2. If it is a work in progress, say so in a comment at the top and record what it is for.
