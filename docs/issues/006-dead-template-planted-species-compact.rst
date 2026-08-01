======================================================
Issue 006: Dead template: planted-species-compact.html
======================================================

:Status: Fixed
:Severity: Low
:Area: templates / cleanup
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: ``kasvimuseo/tests/test_templates.py`` -- it covered the live path
    instead, and said nothing about which file that path uses, so the deletion
    would have gone unnoticed either way.
    ``test_both_species_reports_render_from_the_one_sheet_template``, added
    with the fix, is the assertion that closes that gap
:Depends on: (none)
:Blocks: (none)
:Related: 045 -- ``mobile-base.html``, added here, is the mobile front end that
    was never built
:Decision: Delete both, ruled by the maintainer on 2026-08-01 from the evidence
    below. Neither file is reachable, neither would render correctly if it
    were, and each is superseded by something that exists: the compact report
    by ``planted-species.html`` on ``planted-species-base-compact.html``, and
    the mobile front end by nothing that was ever built. The two were offered
    separately in case the evidence differed; it does not, so one ruling covers
    both
:Resolution: 77f382e -- both files deleted, plus the assertion that pins which
    template the live compact report is rendered from

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

Decision
========

Option 1, on both files. What the report asserted was re-checked rather than
taken, because "nothing references it" is the whole case for deleting
something and a template can be reached by name from another template rather
than from Python.

**Nothing names either file.** ``grep -rn
'planted-species-compact\|mobile-base'`` over the whole working copy matches
only ``docs/issues/*.rst`` and three live things that are not these files: the
URL name ``planted-species-compact`` in ``kasvimuseo/urls.py``, the
``{% url %}`` tags in ``planted-species-list.html`` and
``planted-species-base-compact.html`` that reverse it, and the tests that
request it. The file names themselves --
``planted-species-compact.html``, ``mobile-base.html`` -- appear in no ``.py``,
no ``.html``, nothing under ``static/`` and no test. Every
``{% extends %}`` and ``{% include %}`` in the repository's fifteen templates
was read: seven of them, none naming either file.

**Neither shadows nor is shadowed.** The app-directory loader is active
(issue 024), so a same-named template in an installed package would decide
which file the loader hands back. ``find / -name mobile-base.html -o -name
planted-species-compact.html`` inside the development image, with the working
copy mounted, finds nothing at all: there is one copy of each name, and it is
the one being deleted.

**The compact report is** ``planted-species.html``. ``PlantedSpeciesCompact``
sets only ``base_template_name = 'planted-species-base-compact.html'`` and
inherits ``template_name = 'kasvimuseo/reports/planted-species.html'`` from
``PlantedSpecies`` (``views.py``). So the dead file is the *ancestor* of the
live one rather than a variant of it: it still carries ``{% extends
"jqm/simple.html" %}`` hard-coded, which is exactly what the ``base_template``
context variable replaced when the printable and compact reports were made two
bases over one sheet.

**It would not work if it were wired up.** The live view puts every per-species
value under ``pages``, and this file mixes ``{{ species.name_fi }}`` and
``{{ species.photo.get_display_url }}`` at the top level with ``{{ page.beds }}``
and ``{{ page.origins }}`` -- so under the context the view actually builds,
the names and the photo would come out empty while the beds rendered. Django
silences the mismatch rather than raising, which is what let it sit there
looking load-bearing.

**mobile-base.html could never have rendered.** Eleven lines, an empty
``<body>``, and one template tag -- ``{{ block title }}`` -- which is not
Django syntax and would print literally. It loads jQuery Mobile 1.0b2 from a
CDN. Its whole history is two commits, the first of them "WIP with planted
species report based on jQuery Mobile", and nothing has ever extended it. Issue
045 had already declined to put the viewport tag in it on these grounds.

Nothing was kept as a work in progress, because neither is one: the compact
sheet's work was finished somewhere else, and the mobile front end's was never
started.

Verification
============

**The suite passes**: ``dev/kasvimuseo app test`` -- 426 passed. The branch
adds two of those, the parameters of the new assertion; measured on its own
tree before rebasing it was 415 against a baseline of 413, and the rest
arrived with ``master``.
``dev/kasvimuseo app browser-test`` passes too -- 16 passed -- which this
change cannot reach but the pull request's CI runs anyway.

**The new assertion is the point.** Nothing pinned which template file the
compact URL renders from, so the suite would have stayed green whichever of
the two files had been deleted -- the failure mode this issue is about, one
step removed. ``test_both_species_reports_render_from_the_one_sheet_template``
reads ``response.templates`` for both reports and asserts the sheet, the right
base, and the absence of the deleted name.

**The greps are down to the assertion.** From the repository root::

    $ git grep -n 'planted-species-compact\.html\|mobile-base' -- . ':!docs'
    kasvimuseo/tests/test_templates.py:174: ... ``reports/planted-species-compact.html``
    kasvimuseo/tests/test_templates.py:186: assert '...planted-species-compact.html' not in names

``mobile-base`` is gone from the tracked tree entirely. The two remaining
matches are the new test's ``not in`` assertion and the docstring line that
explains it -- the one place the name is *supposed* to survive, since its
whole job is to fail if that file ever comes back as the live template.
``git grep`` rather than ``grep -rn`` for the reason issue 020 records:
``.dev/docs/html/`` is untracked Sphinx output, and once this page has been
built its own filename matches.

**The page still renders in the running application**, which is the check the
suite cannot make on its own here, since the point of the issue is that the
live path uses a different file. The production dump restored and migrated
forward (``db restore`` then ``app manage migrate``; without the second step
the species pages ``500`` on ``photo_is_horizontal``, see issue 020),
then over HTTP, both reports so the pair can be compared::

    GET /kasvimuseo/planted-species-compact/116,83/    200, 12,616 bytes
    GET /kasvimuseo/planted-species-printable/116,83/  200, 11,086 bytes

Both carry the species' Finnish names, the ``header`` class, the "Yleistietoja
kasvilajista" table, the viewport tag and the print button. Only the compact
one has ``navbar-species-name``, the previous/next bar that lives in the
compact base -- which is what shows the two pages really are the one sheet
under two different bases, rather than the check passing on the wrong page.

**The documentation builds**: ``dev/kasvimuseo docs --clean`` clean, with
warnings as errors, and ``next.rst`` moves 006 out of "Ready now" into "Not in
the queue" with "Status is Fixed" as the reason.

``actionlint`` on ``.github/workflows/tests.yml`` reports two ``SC2012``
informational notes, on the two ``ls /usr/lib/postgresql`` lines. Both are on
``master`` already and this branch does not touch the file.
