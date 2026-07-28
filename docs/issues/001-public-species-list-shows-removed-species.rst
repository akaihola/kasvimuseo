====================================================
Issue 001: Public species list shows removed species
====================================================

:Status: Open
:Severity: High
:Area: models / public site
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_models.py::test_species_manager_ignores_removal_date, kasvimuseo/tests/test_views.py::test_planted_species_list_shows_only_public_planted
:Decision: undecided
:Resolution: (none yet)

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
