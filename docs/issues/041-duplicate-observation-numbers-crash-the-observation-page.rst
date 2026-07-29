===================================================================
Issue 041: Duplicate observation numbers crash the observation page
===================================================================

:Status: Open
:Claimed: branch ``feature/fix-issues-041-and-0-o51``
:Severity: Medium
:Area: views / public site
:Reported: 2026-07-28
:Source: Dashboard walkthrough, branch ``dashboard-usability``
:Evidence: ``kasvimuseo/tests/test_views.py`` covers the view with unique ids only
:Depends on: (none)
:Blocks: (none)
:Related: 007 -- the same family of missing lookup guards on the public views
    009 -- the same ``external_id`` column, seen from the admin side
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``kasvimuseo.views.planted_observation`` looks its object up by museum
number::

    observation = get_object_or_404(Observation,
                                    external_id=observation_external_id)

``Observation.external_id`` carries no uniqueness constraint, and the
production data has duplicates. In the July 2026 dump, of 311 observations
(none with a null number) 307 numbers are distinct: 147, 1092, 1172 and 1291
each appear twice. Requesting one of those numbers raises
``MultipleObjectsReturned`` -- a 500, not the 404 the ``get_object_or_404``
was reaching for.

The view had no link anywhere in the application until now, which is why this
has never been seen. The ``sivu`` column added to the observation changelist
in the same change makes it reachable, so roughly 3 % of those links now lead
to an error page.

Impact
======

Eight of 311 observations have an unreachable public page. The rest work. A
gardener clicking the link sees Django's error page, with no hint that the
cause is two rows sharing a number.

Options
=======

1. Decide what a duplicate number means and make the view say it -- take the
   first match, or render both observations on the page the way the species
   sheet renders several species. This is a product question: if two rows
   share a number, is that one plant recorded twice or two plants numbered
   wrongly?
2. Clean the data and add ``unique=True``, which turns the crash into a
   migration that fails loudly until the four collisions are resolved.
3. Key the URL by primary key instead. The route is new to the UI and no
   external links exist to preserve, so the change is cheap -- but the museum
   numbering is what the staff know the plants by.

Whichever is chosen, the ``sivu`` link should stop pointing at an error page.

See also
========

Issue 007 (an unknown species id renders an empty page instead of a 404) --
the same family of missing lookup guards on the public views. Issue 009
(``Create Species Sheets`` breaks without an ``external_id``) is the same
column seen from the admin side.
