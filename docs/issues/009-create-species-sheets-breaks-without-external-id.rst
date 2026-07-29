========================================================================
Issue 009: Create Species Sheets breaks on a species with no external id
========================================================================

:Status: Fixed
:Severity: Medium
:Area: admin
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_admin.py::test_planted_species_report_with_null_external_id
:Depends on: (none)
:Blocks: (none)
:Related: 041 -- the same ``external_id`` column, seen from the admin side
    007 -- the same family of missing lookup guards
:Decision: Option 1 -- skip the species that have no external id, name them in
    an admin message, and report on the rest. It is the only option that needs
    no ruling: option 2 would refuse work the gardener can have, and option 3
    is a data migration against production data that is not available here, so
    it is the maintainer's to decide.
:Resolution: Fixed in COMMIT.

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

Fix
===

``planted_species_report`` now excludes ``external_id IS NULL`` from the URL it
builds and reports the excluded species by name through
``modeladmin.message_user``, matching the guard ``ObservationAdmin.page``
already applies to the same column. When *every* selected species lacks an id
there is nothing to report on, so the action says so and returns without
redirecting, leaving the changelist where it was.

Issue 023 notes that ``django.contrib.messages`` is not in ``INSTALLED_APPS``,
which made ``message_user`` worth checking before relying on it. It works:
what the framework needs to deliver a message is ``MessageMiddleware``, and
these settings define no ``MIDDLEWARE_CLASSES`` at all, so Django's default --
which includes it -- applies. ``test_planted_species_report_through_the_admin``
pins that end to end, posting the action through the admin and finding the
message on the page the redirect leads back to. 023 is untouched here; if it is
fixed by adding the app *and* an explicit middleware list, that list must keep
``MessageMiddleware`` or this action goes silent.
