==============================================================
Issue 053: The museum numbers on a label come in any order
==============================================================

:Status: Fixed
:Severity: Low
:Area: views / labels API
:Reported: 2026-07-31
:Source: Browser suite built for issue 017, first run
:Evidence: kasvimuseo/tests/test_views.py::test_labels_api_get_orders_the_museum_numbers_on_a_label
    -- written with the fix, with
    ``test_labels_api_get_puts_a_missing_number_first`` for the missing
    number and
    ``test_labels_api_post_round_trips_the_museum_numbers_in_order`` for the
    path a saved label takes; all three fail on the old handler
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- its browser suite is what found this
    010 -- the same handler, and the other half of the save round trip
    039 -- the same ``get_species_data``, whose signature it last changed
    009 -- the same nullable ``external_id``, from the admin side
:Decision: Sort by the museum number itself, as a number, with an observation
    that has none first: ``sorted(observation_set, key=attrgetter('external_id'))``.
    The maintainer was asked to choose between first, last and excluded and
    between numeric and string ordering, and the question did not reach anyone,
    so it is ruled on the evidence. **Numeric** because the column is an
    ``IntegerField`` and production ids run from 1 to 1314, so a text sort would
    read 1, 11, 12, 1314, 2 -- a different wrong order rather than a fix -- and
    because the two places that already sort this same list sort numerically.
    **First** because that is where those two places already put a missing one:
    ``kasvimuseo_model_tags.external_ids`` calls ``sorted()`` on the values,
    and Python 2 sorts ``None`` before every integer, while the editor's
    ``insort`` compares with ``<``, and in JavaScript ``null < 5`` is true. Last
    would have been the nicer sheet but would have meant changing all three to
    keep one order; excluded would have hidden a row that the ``post`` handler
    then cannot re-link. **Nothing in reach has the case anyway**: the
    production dump in ``.dev/backups/production.sql`` has 311 observations and
    0 without an ``external_id`` -- 009's precedent is the same column on
    ``Species``, and that has none either -- and every observation in
    ``browser_tests/seed.py`` has one. So the ruling costs nothing today and
    only says what happens when the nullable column is finally used.
:Resolution: Fixed in 6f431cd.

Problem
=======

``PlantedSpeciesLabelsApi.get_labels_data`` grouped the observations by species
and sorted each group::

    observations_by_species = OrderedDict([
        (species, sorted(observation_set))
        for species, observation_set
        in groupby(queryset, attrgetter('species'))])

``sorted()`` with no ``key`` sorts the ``Observation`` instances themselves.
The model defines no comparison methods, and its ``Meta.ordering`` is
``species__name_fi``, which says nothing about two observations *of the same
species* -- exactly the ones that share a label. Python 2 falls back to
comparing the objects by address, so the order of the numbers on a label is
whatever the objects happen to sit at in memory.

There are two ways into the entry, and the other one did not sort at all. Once
a ``Label`` exists, the numbers come from its plantings::

    [planting.observation for planting in label.planting_set.all()]

and ``Planting.Meta.ordering`` is ``observation__species__name_fi``, which is
constant within a label. That is the path taken *after* a save, which is why
the same label can print "12 11" and then "11 12" once somebody has dragged a
number: the editor's own ``insort`` keeps its list in numerical order, so what
the browser shows and what the next GET returns are two different orders.

Impact
======

Cosmetic on a printed label, and it is a sheet people read numbers off: a
label with several numbers on it has no reliable order, and the order changes
between renders and after a save. Nothing is lost and nothing crashes.

Options
=======

1. Sort by ``external_id``, missing numbers first -- one key expression, the
   order the templatetag and the editor already produce.
2. Sort by ``external_id``, missing numbers last -- reads better on paper, but
   the templatetag and the editor's ``insort`` have to change with it or the
   browser and the server disagree after a save.
3. Leave out the observations that have no ``external_id`` -- hides a row that
   exists, and ``post`` re-links plantings by ``external_id``, so an excluded
   observation quietly loses its label on the next save.
4. Give ``Observation`` a ``Meta.ordering`` of ``('species__name_fi',
   'external_id')`` instead -- fixes the grouped queryset but not the label's
   ``planting_set``, so it leaves the save round trip unsorted.

Fix
===

Option 1, applied once in ``get_species_data`` rather than in each of its two
callers, so both ways into a label produce the same order::

    observations = sorted(observation_set, key=attrgetter('external_id'))

``get_labels_data`` keeps materialising each ``groupby`` group -- ``list()``
now, where ``sorted()`` used to do it as a side effect -- because a group is
invalidated the moment the next one is asked for. ``nicknames`` is built from
the same sequence as ``external_ids``, so the two lists stay aligned.

No query changes, so ``test_labels_api_get_reads_the_label_photo_without_more_queries``
still counts 14.
