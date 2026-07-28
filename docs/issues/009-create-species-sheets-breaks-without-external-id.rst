========================================================================
Issue 009: Create Species Sheets breaks on a species with no external id
========================================================================

:Status: Open
:Severity: Medium
:Area: admin
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_admin.py::test_planted_species_report_with_null_external_id
:Decision: undecided
:Resolution: (none yet)

Problem
=======

The ``planted_species_report`` admin action joins the selected species' ``external_id``
values into a URL::

    external_ids_param = u','.join(unicode(external_id) for external_id in external_ids)
    url = reverse('planted-species', kwargs={'species_external_ids': external_ids_param})

``Species.external_id`` is nullable. For a species without one, ``unicode(None)`` is
``'None'``, which the URL pattern ``[\d,]+`` rejects, so ``reverse`` raises
``NoReverseMatch``.

Impact
======

Selecting a species that has no external id and running the action gives a 500 instead of a report.

Options
=======

1. Skip species with no external id, and tell the user which were skipped.
2. Refuse the action with a message when any selected species lacks an id.
3. Give every species an external id and make the field non-nullable -- a data migration.
