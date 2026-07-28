=============================================================
Issue 004: Broken placeholder image on every observation page
=============================================================

:Status: Open
:Severity: Medium
:Area: templates / public site
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py
:Decision: undecided
:Resolution: (none yet)

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
