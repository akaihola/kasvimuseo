===============================================================
Issue 008: Photologue gallery index raises on an empty database
===============================================================

:Status: Open
:Severity: Medium
:Area: urls / third party
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_project_urls.py (proves the include another way)
:Depends on: (none)
:Blocks: (none)
:Related: 018 -- a CI job starting from a fresh database is what would catch this
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``GET /photologue/gallery/`` raises rather than rendering when there are no galleries:
it is a date-based archive view with ``allow_empty`` off. A fresh database created by
``dev/kasvimuseo db bootstrap`` has no galleries, so the page is a 500 for any new
developer, and for the site until the first gallery exists.

Impact
======

A 500 on a URL reachable from the admin, on any database with no galleries.

Options
=======

1. Create a gallery as part of the bootstrap fixtures.
2. Override the photologue URL with ``allow_empty=True``.
3. Leave it, and note in the README that the gallery index needs at least one gallery.
