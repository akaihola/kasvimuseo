==================================================================
Issue 007: Unknown species id renders an empty page instead of 404
==================================================================

:Status: Fixed
:Severity: Low
:Area: views / public site
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py --
    ``test_unknown_external_id_404s`` (was
    ``test_unknown_external_id_renders_an_empty_report``, which pinned the empty
    200) and ``test_partly_unknown_external_id_still_renders_what_matched``
:Depends on: (none)
:Blocks: (none)
:Related: 041 -- the same family of missing lookup guards on the public views
:Decision: Option 1 -- raise ``Http404`` when *nothing* in the list matches
:Resolution: Fixed in ``kasvimuseo/views.py``, commit b4266bd

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

Decision
========

Option 1, narrowed to exactly the case option 3 calls questionable: the view
404s only when *no* id in the list matches anything. A list where some ids match
still renders those, as before, so the report a member of staff builds from a
selection does not disappear because one species has been renumbered. Option 2
would need a template and a translated string for a page nobody should reach by
following a working link; a 404 is what a dead link deserves, and it keeps
search engines from indexing the empty page.

Resolution
==========

``PlantedSpecies.get`` checks ``queryset.exists()`` before building the context
and raises ``Http404`` when it is empty. The check costs one extra query only on
the empty path -- Django evaluates the queryset for the context anyway.
``kasvimuseo/tests/test_templates.py`` replaces
``test_unknown_external_id_renders_an_empty_report`` with
``test_unknown_external_id_404s``, and adds
``test_partly_unknown_external_id_still_renders_what_matched`` to pin the
partial-match case the decision deliberately leaves alone. Commit b4266bd.
