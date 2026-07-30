=============================================================
Issue 012: public_planted issues one COUNT query per planting
=============================================================

:Status: Fixed
:Severity: Medium
:Area: models / performance
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_models.py (query counts asserted around the managers)
:Depends on: (none)
:Blocks: 001 -- fix the query cost before changing what the loop means
:Related: 001 -- the same ``any(...)`` loop
:Decision: fix the real per-planting query, which is not the one in the title
:Resolution: ``ObservationManager`` now prefetches ``planting_set__bed``, and
             ``is_public_planted`` reads ``last_care`` instead of counting the
             care rows first

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

What it actually was
====================

The diagnosis above is wrong, and measuring it says so. A prefetched
``care_set.count()`` costs **zero** queries: Django 1.5's ``QuerySet.count()``
returns ``len(self._result_cache)`` when the cache is populated, and that is
exactly what ``prefetch_related`` populates. Counting the queries around a
prefetched loop of three plantings gives 0, not 3.

The query that really scaled per planting was ``kasvimuseo_bed``.
``is_public_planted`` opens with ``self.bed.public``, and ``bed`` is an
unfetched foreign key, so each planting fetched its own bed row.
``PlantingManager`` was already immune -- it has ``select_related('bed__public')``
-- which is why only ``ObservationManager`` grew. ``SpeciesManager`` never
touches ``bed``, so it was flat all along.

Measured, going from 2 to 6 plantings:

==================  ===========  ==========
Manager             before       after
==================  ===========  ==========
``Species``         5 -> 5       5 -> 5
``Observation``     6 -> 10      5 -> 5
``Planting``        3 -> 3       3 -> 3
==================  ===========  ==========

Fix
===

``ObservationManager.public_planted`` prefetches ``planting_set__bed`` alongside
``planting_set__care_set``. That alone flattens the query count, and takes the
labels API from 16 queries to 14
(``test_labels_api_get_reads_the_label_photo_without_more_queries``).

``is_public_planted`` also dropped its ``care_set.count()``, which was a real
extra query on the *unprefetched* path -- a plain
``Planting.objects.get(...).is_public_planted()`` on a planting with care rows
cost 4 queries and now costs 3. It reads ``last_care`` instead, keeping the
``removal_date`` short circuit ahead of it so a removed planting still costs 2.

``SpeciesManager`` was left alone: swapping its prefetched ``.count()`` for
``len(...all())`` changes nothing under the prefetch and is worse without it.

``test_public_planted_query_count_does_not_grow_with_the_plantings`` pins the
flat count; it fails on the old code. The visibility matrix is unchanged --
all four outcomes (no cares, last care above zero, last care zero, removed)
return what they did before.
