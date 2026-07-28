=============================================================
Issue 012: public_planted issues one COUNT query per planting
=============================================================

:Status: Open
:Severity: Medium
:Area: models / performance
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_models.py (query counts asserted around the managers)
:Depends on: (none)
:Blocks: 001 -- fix the query cost before changing what the loop means
:Related: 001 -- the same ``any(...)`` loop
:Decision: undecided
:Resolution: (none yet)

Problem
=======

All three ``public_planted`` managers call ``prefetch_related`` to load the care
records, and then defeat it by calling ``.count()`` on the prefetched manager::

    if any(planting.care_set.count() == 0
           or planting.last_care_count() > 0 ...

``care_set.count()`` issues a fresh ``COUNT`` query rather than using the prefetched
cache, so the cost is one extra query per planting.
``Planting.is_public_planted`` does the same, and ``ObservationManager`` and
``PlantingManager`` reach it through that.

``Planting.last_care`` shows the intended pattern: it checks
``_prefetched_objects_cache`` and sorts in Python when the data is already loaded.

Impact
======

The public species list and the labels API scale their query count with the number of plantings. The docstrings already warn "NB! This evaluates the queryset!".

Options
=======

Use ``len(planting.care_set.all())`` -- which consumes the prefetched cache -- or apply
the same ``_prefetched_objects_cache`` check ``last_care`` already uses. Behaviour should
not change; the tests pin the current results.
