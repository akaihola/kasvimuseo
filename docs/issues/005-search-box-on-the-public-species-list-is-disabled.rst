============================================================
Issue 005: Search box on the public species list is disabled
============================================================

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

``reports/planted-species-list.html`` builds a jQuery Mobile listview whose filter
attributes are all prefixed with an ``X``, which stops jQuery Mobile from seeing them::

    <ul data-role="listview"
        Xdata-filter="true"
        Xdata-filter-placeholder="Etsi kasvin nimellä..."
        Xdata-filter-theme="b">

So the "Etsi kasvin nimellä..." search box never appears.

Impact
======

Visitors cannot search the public species list. The placeholder text shows the feature was built and then switched off.

Options
=======

1. Drop the ``X`` prefixes to turn the search back on, if it was disabled by accident
   or as a temporary measure.
2. Delete the attributes entirely if the search was removed deliberately, so the next
   reader does not have to guess.
