=============================================================
Issue 004: Broken placeholder image on every observation page
=============================================================

:Status: Fixed
:Severity: Medium
:Area: templates / public site
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py --
    ``test_observation_page_has_no_placeholder_image`` now pins the fixed
    behaviour, next to the two tests that already read this page
:Depends on: (none)
:Blocks: (none)
:Related: 011 -- option 2 here renders the species photo, which is what 011 is about
:Decision: Option 1 -- remove the tag
:Resolution: Fixed in 170412f.

Problem
=======

``kasvimuseo/templates/kasvimuseo/reports/planted-observation.html`` line 13 contains a
hardcoded placeholder::

    <img src="dummy.jpg" />

There is no such file, so every observation page renders a broken image.

Impact
======

A visible broken image on every per-observation page.

Options
=======

1. Remove the tag.
2. Replace it with the observation's real photo if one was intended here -- the page has
   access to the species photo used by the species report.

Decision
========

Option 1. The tag came in with the page itself, in d541468 ("Added the planted
species and observations reports"), pointing at a filename that has never
existed anywhere in this repository: it is scaffolding that was left behind, not
a photo that went missing. Removing it is the only change that restores the page
to what it already renders, which is what the issue asks for.

Option 2 is a feature rather than a fix, and it is not free here: the species
report's photo markup is the code 011 is about -- it opens every image file on
every render to choose a CSS class -- so adding a photo to this page before 011
is settled would copy that cost onto a second page. If the observation page
genuinely wants a photo, that is worth filing as its own item once 011 has a
ruling; nothing in the page's markup or history says it does.

Resolution
==========

The one line is gone from
``kasvimuseo/templates/kasvimuseo/reports/planted-observation.html``, and
``kasvimuseo/tests/test_templates.py`` gains
``test_observation_page_has_no_placeholder_image``, which asserts both that
``dummy.jpg`` is absent and that the page carries no ``<img>`` at all -- so
option 2 cannot be added by accident without the test being changed
deliberately. Commit 170412f.
