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
:Related: 045 -- ``mobile-base.html``, added here, is the mobile front end that
    was never built
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``reports/planted-species-compact.html`` is 165 lines and nothing references it. A grep
across ``.py`` and ``.html`` finds no user. ``PlantedSpeciesCompact`` renders
``reports/planted-species.html`` with ``planted-species-base-compact.html`` as its base.

It is also internally inconsistent: it mixes top-level ``{{ species.* }}`` with
``{{ page.beds }}``, so if it were ever wired up the names and photo would render empty.

``ylaneenkasvit/templates/mobile-base.html`` is the same kind of leftover, found
while looking into issue 045. Nothing references it either, its ``<body>`` is
empty, and its one template tag -- ``{{ block title }}`` -- is not Django syntax,
so it could never have rendered. It loads jQuery Mobile 1.0b2 from a CDN, which
dates it to 2011 and marks it as the abandoned start of a mobile front end.

Impact
======

165 lines that look load-bearing but are not, and would misbehave if used. Plus
a second, smaller template that reads as evidence of a mobile site that does not
exist.

Options
=======

1. Delete both.
2. If either is a work in progress, say so in a comment at the top and record
   what it is for.
