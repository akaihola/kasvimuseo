==================================================================
Issue 007: Unknown species id renders an empty page instead of 404
==================================================================

:Status: Open
:Claimed: branch ``feature/fix-issues-041-and-0-o51``
:Severity: Low
:Area: views / public site
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py::test_unknown_external_id_renders_an_empty_report
:Depends on: (none)
:Blocks: (none)
:Related: 041 -- the same family of missing lookup guards on the public views
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``PlantedSpecies.get`` filters species by the external ids in the URL and renders
whatever comes back. For an id that matches nothing the queryset is empty, so the page
returns 200 with an empty ``<article>`` and a navigation bar, rather than a 404.

Impact
======

A wrong or stale link gives a blank page rather than a clear "not found", and search engines index the empty page as valid.

Options
=======

1. Raise ``Http404`` when the queryset is empty.
2. Render an explicit "no such species" message.
3. Accept it -- the view takes a comma-separated list, so a partial match is legitimate;
   only the fully empty case is questionable.
