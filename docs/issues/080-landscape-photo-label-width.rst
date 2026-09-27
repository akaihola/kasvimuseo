Issue 080: The label under a landscape photo is too narrow
==========================================================

:Status: Fixed
:Severity: Medium
:Area: templates / public species
:Reported: 2026-09-27
:Source: Maintainer report in ``docs/issues/incoming.rst``
:Evidence: ``browser_tests/test_species_report.py`` checks widths in both orientations.
:Depends on: (none)
:Blocks: (none)
:Related: (none)
:Decision: Set the compact image to the header width. Keep each orientation's existing header width.
:Resolution: 91efc41 aligns the outer label border with both photo edges.

Problem
=======

On the planted species compact view, the label below a landscape photo is too
narrow. The label matches portrait photos. Its borders must match the photo
borders for both orientations.

Work
----

The photo and label are rendered by
``kasvimuseo/templates/kasvimuseo/reports/planted-species.html``. Their widths
are set in ``static/css/planted-species-printable.css``. Fix the width rule and
add a focused regression check.

Checks
------

Run these commands from the repository root::

    dev/kasvimuseo app browser-test browser_tests/test_species_report.py
    dev/kasvimuseo app test kasvimuseo/tests/test_templates.py
    dev/kasvimuseo docs

Results on 2026-09-27:

* The browser check passed four cases in Chromium and WebKit. Both orientations passed in each engine. The run needed a temporary ``django.setup()`` before model imports in ``browser_tests/seed.py``. That file remains unchanged. See ``.agents/memory/browser-test-seed-needs-django-setup.md``.
* The template suite passed 56 tests.
* The documentation build passed.
* The full suite stopped during collection. ``test_media_fetch.py`` has a Python 2 encoding error, and ``test_photos.py`` cannot import ``mock``.
