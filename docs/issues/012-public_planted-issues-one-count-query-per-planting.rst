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
:Decision: Follow ``last_care``'s idiom, by reusing ``last_care`` itself in
           ``is_public_planted`` rather than writing a second
           ``_prefetched_objects_cache`` check, and read the prefetched rows
           with ``len(...all())`` in ``SpeciesManager``. Then fix the query
           that actually scaled per planting, which is not the ``COUNT`` in
           the title but the ``bed`` behind ``is_public_planted``. Call paths
           checked: ``ObservationManager.public_planted`` and
           ``PlantingManager.public_planted`` (the only two in the codebase
           that reach ``is_public_planted``), the four views that reach those
           managers, and a lone ``Planting.objects.get(...)`` outside any
           prefetch -- the last is one query cheaper, not dearer.
:Resolution: commits c3a46b5 (``ObservationManager`` prefetches
             ``planting_set__bed``; ``is_public_planted`` reads ``last_care``)
             and 426d855 (``SpeciesManager`` reads the prefetched rows with
             ``len(...all())``; call paths audited)

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

``SpeciesManager`` uses ``len(planting.care_set.all())``, the idiom this issue
asked for. It costs nothing there either way -- the ``.count()`` it replaces
was already free -- but it says plainly that the loop reads rows the method
itself prefetched. It needs no ``_prefetched_objects_cache`` guard: the
``prefetch_related`` is two lines above it, so there is no unprefetched way
into that loop. That guard matters only where a caller might arrive without a
prefetch, which is exactly ``is_public_planted``, and there it comes for free
by delegating to ``last_care``.

Call paths checked
==================

``is_public_planted`` has two callers in the codebase, both inside managers
that already load what it reads:

==================================  ==================================
Caller                              How the ``bed`` and cares arrive
==================================  ==================================
``ObservationManager``              ``prefetch_related`` (bed added here)
``PlantingManager``                 ``select_related('bed__public')``
==================================  ==================================

Reaching those: ``PlantedSpeciesList`` and the species detail page use
``SpeciesManager``; the labels API uses ``ObservationManager`` on ``GET`` and
``PlantingManager`` on ``POST``. No template, admin or view calls
``is_public_planted`` directly.

The remaining path is a ``Planting`` loaded on its own, which the tests do and
a shell or a future caller might. It is the one the issue warns could be
pessimised by consuming a prefetch cache, so it is measured rather than
argued: with care records it costs 3 queries where it cost 4, because the
``COUNT`` it dropped was followed by the same row fetch anyway. A removed
planting still costs 2 -- ``removal_date`` short circuits before ``last_care``
is touched. ``len(...all())`` is deliberately *not* used on this path.

Tests
=====

``test_public_planted_query_count_does_not_grow_with_the_plantings`` pins the
flat count at two planting counts, and
``test_is_public_planted_unprefetched_is_correct_and_no_more_expensive`` pins
the lone-``Planting`` path, result and cost, across all four outcomes. Both
fail on the pre-fix code. No assertion about *results* was edited: the
visibility matrix is unchanged, and the one number that moved is the labels
API's query count in
``test_labels_api_get_reads_the_label_photo_without_more_queries``, 16 to 14.
