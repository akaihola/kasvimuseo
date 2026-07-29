===================================================================
Issue 041: Duplicate observation numbers crash the observation page
===================================================================

:Status: Fixed
:Severity: Medium
:Area: views / public site
:Reported: 2026-07-28
:Source: Dashboard walkthrough, branch ``dashboard-usability``
:Evidence: ``kasvimuseo/tests/test_views.py`` --
    ``test_planted_observation_renders_the_first_of_a_duplicated_number`` and
    ``test_planted_observation_404s_when_no_observation_carries_the_number``
    now cover the duplicate case the suite previously reached with unique ids
    only
:Depends on: (none)
:Blocks: (none)
:Related: 007 -- the same family of missing lookup guards on the public views
    009 -- the same ``external_id`` column, seen from the admin side
:Decision: Option 1, in its cheapest form -- the first match by primary key.
    ``Status: Fixed`` covers the crash only: this stops it without ruling on
    what a duplicate museum number *means*, which is still open. See
    "Decision" and "Still open" below
:Resolution: Fixed in ``kasvimuseo/views.py``, commit b4266bd

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

Decision
========

Option 1, taking the first match. It is the only one of the three that stops
the crash today without deciding anything else, and the crash is the part that
is live: the ``sivu`` link now answers on all 311 observations.

Option 2 was rejected here because it needs the production data to clean, which
this environment does not have (issue 026 is the reason it is not available),
and because ``unique=True`` is the answer to the product question rather than a
way of avoiding it -- the migration cannot be written before somebody says which
of the two rows in each pair keeps the number. Option 3 was rejected because the
museum number is what the staff know the plants by, and a URL keyed by primary
key cannot be typed or read from a label.

"First" is ordered by primary key explicitly. The lookup has no default
ordering, so without ``order_by`` the row PostgreSQL happens to return could
differ between requests -- the same number showing two different plants would be
worse than the crash it replaced.

Resolution
==========

``planted_observation`` filters, orders by ``pk`` and takes the first row,
raising ``Http404`` when there is none, in place of the ``get_object_or_404``
that raised ``MultipleObjectsReturned``. ``kasvimuseo/tests/test_views.py`` gains
a duplicate-number test that asserts a 200 and the same observation across two
requests, and a second unknown-number test that pins the 404 with other
observations present. Commit b4266bd.

Still open
==========

What a duplicate museum number means. If two rows sharing a number are one plant
recorded twice, the duplicate should be merged; if they are two plants numbered
wrongly, one of them should be renumbered -- and either way the column should
then carry ``unique=True`` (option 2), which would make this view's guard dead
code rather than wrong. Until that ruling, the second observation of each of the
four pairs has no public page of its own, which is a smaller fault than the one
it replaces but is still a fault. Deciding it needs the production data.

See also
========

Issue 007 (an unknown species id renders an empty page instead of a 404) --
the same family of missing lookup guards on the public views. Issue 009
(``Create Species Sheets`` breaks without an ``external_id``) is the same
column seen from the admin side.
