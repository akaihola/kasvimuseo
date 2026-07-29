============================================================
Issue 005: Search box on the public species list is disabled
============================================================

:Status: Fixed
:Severity: Medium
:Area: templates / public site
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py --
    ``test_species_list_offers_the_jquery_mobile_search_box`` now pins the fixed
    behaviour, next to the three tests that already read this list
:Depends on: (none)
:Blocks: (none)
:Related: (none)
:Decision: Option 1 -- drop the ``X`` prefixes
:Resolution: Fixed in 59b6a92.

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

Decision
========

Option 1. The history says the search was never switched *off*: the prefixes
arrived with the file itself, in 14464ba ("WIP with planted species report based
on jQuery Mobile", 2011), which is the only commit ``git log -S 'Xdata-filter'``
finds. That first version prefixed the loop variable the same way --
``{% for species in object_listX %}`` -- which is what the ``X`` is: a
work-in-progress marker for "not this line yet", used while the page was being
built against a listview that had no data. The ``object_listX`` was unprefixed
once the view fed it; these three were forgotten. Nothing in the 15 years since
touches them, and no commit message, comment or issue records the search as
broken. Option 2 would delete a feature on the strength of a typo.

jQuery Mobile is genuinely on the page, so the un-prefixed attributes do
something: the template extends ``jqm/simple.html`` from ``django-jqm``
(``requirements/production.txt``), whose base ``jqm/v1_1_0.html`` loads jQuery
1.7.2 and jQuery Mobile 1.1.0 from ``code.jquery.com``. Listview filtering is a
1.0 feature, so 1.1.0 reads ``data-filter``, ``data-filter-placeholder`` and
``data-filter-theme`` and builds the search box above the list.

Resolution
==========

Three characters gone from
``kasvimuseo/templates/kasvimuseo/reports/planted-species-list.html``, and
``kasvimuseo/tests/test_templates.py`` gains
``test_species_list_offers_the_jquery_mobile_search_box``, which asserts the
three attributes reach the delivered page and that no ``Xdata-filter`` remains.
What the test cannot reach is the box itself: it is drawn by jQuery Mobile in
the browser, so the assertion stops at the contract with it -- the rest wants
the browser suite that 017 is about. Commit 59b6a92.
