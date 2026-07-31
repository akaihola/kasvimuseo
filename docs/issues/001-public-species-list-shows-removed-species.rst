====================================================
Issue 001: Public species list shows removed species
====================================================

:Status: Fixed
:Severity: High
:Area: models / public site
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_models.py::test_species_manager_honours_removal_date_and_the_bed (named test_species_manager_ignores_removal_date while it pinned the defect), kasvimuseo/tests/test_views.py::test_planted_species_list_shows_only_public_planted
:Depends on: 012 -- do the behaviour-preserving query fix first, so the semantic change lands on clean code
:Blocks: (none)
:Related: 012 -- the same ``any(...)`` loop
:Decision: Option 1, chosen by the maintainer: reuse
           ``Planting.is_public_planted`` in ``SpeciesManager`` so all three
           managers agree, accepting that the public list gets shorter. The
           case put to them was that the docstring already promised it --
           "Returns public *currently* planted species", excluding
           observations "which haven't been removed" -- so the check was
           intended and merely absent; that the other two managers already
           behave this way, and the pages a visitor reaches from the list
           already hide the removed planting; and that the inner loop's
           second defect is a leak under either reading of the page, since a
           planting in a *private* bed could keep a species on the *public*
           list. ``kasvimuseo/views.py`` had already taken the same side: the
           species detail page lists beds with
           ``.exclude(removal_date__isnull=False)``.
:Resolution: commit 24d5005 (``SpeciesManager`` applies
             ``is_public_planted`` and prefetches the bed; the pinning test
             rewritten to cover the removed planting and the private-bed one;
             the species query stays flat at 6 queries)

Problem
=======

``SpeciesManager.public_planted`` never looks at ``removal_date``, while
``PlantingManager.public_planted`` and ``ObservationManager.public_planted`` both do,
through ``Planting.is_public_planted``. Two of the three managers agree with each other,
so ``SpeciesManager`` is the odd one out.

It is worse than a missing check. The outer query filters to species that have *some*
planting in a public bed, but the inner ``any(...)`` then iterates **every** planting of
every observation of the species, including plantings in non-public beds::

    if any(planting.care_set.count() == 0
           or planting.last_care_count() > 0
           for observation in species.observation_set.all()
           for planting in observation.planting_set.all()):

So a species whose public plantings have all been removed still appears on the public
species list, kept alive by a planting in a private bed.

Impact
======

Visitors see species that are no longer growing in the garden.

Options
=======

1. Reuse ``Planting.is_public_planted`` in ``SpeciesManager``, making all three
   managers agree. Changes what the public site lists.
2. Decide the current behaviour is intended -- "the garden has held this species" rather
   than "holds it now" -- and document it instead.

The tests currently pin the existing behaviour, so either choice is a deliberate,
visible change; see also issue 012, which is in the same loop.

Fix
===

``SpeciesManager.public_planted`` calls ``planting.is_public_planted()`` --
the whole test, not a second copy of it -- so the three managers cannot drift
apart again. The outer ``filter`` stays: it only narrows the candidates, and
the per-planting check is what decides.

``is_public_planted`` opens with ``self.bed.public``, so
``observation_set__planting_set__bed`` joins the care records in the
``prefetch_related``. That is the omission issue 012 measured in
``ObservationManager``: without it, each planting fetches its own bed row.

What it costs
=============

One query, once. The species manager went from 5 to 6 queries, and the number
does not move with the number of plantings:

==================  ===========  ===========
Manager             2 plantings  6 plantings
==================  ===========  ===========
``Species``         6            6
``Observation``     5            5
``Planting``        3            3
==================  ===========  ===========

``test_public_planted_query_count_does_not_grow_with_the_plantings`` asserts
both columns, so the flatness is pinned rather than assumed. The constant that
moved is the price of reading the bed at all, and it buys the check this issue
is about.

Tests
=====

``test_species_manager_ignores_removal_date`` pinned the defect and is now
``test_species_manager_honours_removal_date_and_the_bed``: a removed planting
is hidden by all three managers, and stays hidden when the same species also
has a live planting in a private bed -- the planting that used to keep it
listed. ``test_public_planted_removed_is_hidden`` gained the ``Species``
assertion it had been missing, and
``test_planted_species_list_shows_only_public_planted`` (the view named in
``Evidence`` above) no longer expects ``poistettu``. Reverting only
``models.py`` fails five tests, so none of the changed assertions is vacuous.
