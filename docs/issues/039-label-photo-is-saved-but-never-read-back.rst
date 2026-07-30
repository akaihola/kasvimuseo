=================================================================
Issue 039: The label photo is saved but never read back
=================================================================

:Status: Fixed
:Severity: Medium
:Area: views / labels API
:Reported: 2026-07-28
:Source: Walkthrough of how photo management is meant to be used
:Evidence: kasvimuseo/tests/test_views.py::test_labels_api_post_round_trips_the_photo_choice
    -- the POST-then-GET round trip the issue asked for, written with the fix
:Depends on: (none)
:Blocks: 037 -- option 3 there depends on what this decides
:Related: 010 -- the same ``post`` handler
    042 -- the control that looks like it should set the species photo
    017 -- the Vue editor has no browser test
:Decision: Option 1, read it back. It is what the code plainly meant to do, it
    needs no migration, and option 2 would delete a capability the maintainer
    has been using by hand before each print run. ``get_species_data`` now takes
    the ``Label`` itself rather than its ``visible`` flag, and passes
    ``label.photo`` to ``get_species_photo_info`` as a new ``photo`` argument
    that wins over ``species.photo``; a species with no label passes ``None``
    and keeps the species photo. The ``Label`` queryset adds ``photo`` to its
    ``select_related``, so the choice arrives on the join: the GET costs 18
    queries for the data in
    ``test_labels_api_get_reads_the_label_photo_without_more_queries`` before
    the change and 16 after, the two saved being the deferred ``species.photo``
    lookups the labels with a photo of their own no longer need. Issue 037 can
    now describe the chevrons as choosing the label's photo, which is its option
    3.
:Resolution: Fixed in c9cb3f5.

Problem
=======

``PlantedSpeciesLabelsApi.post`` stores the photo chosen for each label::

    Label.objects.bulk_create([Label(species_id=item['id'],
                                     photo_id=item['photo_pk'],
                                     visible=item['visible'])
                               for item in items])

``PlantedSpeciesLabelsApi.get_labels_data`` never reads it back. It iterates over the
saved ``Label`` rows, but passes only ``label.visible`` on to ``get_species_data``, and
that function derives the photo from the *species*::

    photo_pk, photo_alternatives = get_species_photo_info(
        species, photo_pks_and_urls_by_title)

``get_species_photo_info`` (``kasvimuseo/photos.py``) looks at ``species.photo``.
``label.photo`` is read nowhere in the application -- only in ``Label.__unicode__``, for
the admin string. Grepping for it finds the model field, the South migration, the
``__unicode__`` and the ``bulk_create`` above; nothing else.

So the chevron buttons on the label editor change the photo on screen, the save writes
the choice to the database, and the next load silently replaces it with the species
photo again. The ``visible`` flag beside it round-trips correctly, which is what makes
the failure hard to spot: saving *appears* to work, because part of it does.

This has been the behaviour since the choice was first persisted. Commit 957e441 ("Fix
#5: Add saving of planting labels grouping and hiding", 2018-04-23) added ``Label``,
extended the read path with ``visible`` and the grouping, and added ``photo_id`` to the
write path -- but left ``get_species_data`` reading ``species.photo``. The photo
selection itself had shipped a week earlier in 8e689a6 ("Fix #13: Allow selecting the
photo for a species label"), before there was anywhere to store it.

Impact
======

Per-label photo choices are lost on every reload, so the printed labels show the species
photo regardless of what was chosen. The user's only remedy is to redo the selection
immediately before each print run, and nothing tells them that is necessary. Stored
``Label.photo`` values accumulate and are never used, so the database records intent the
application ignores.

Options
=======

1. **Read it back.** Pass the label to ``get_species_data`` and prefer ``label.photo``
   over ``species.photo`` when it is set, falling back to the species photo for the
   species that have no ``Label`` row yet. ``select_related('species', 'photo')`` on the
   ``Label`` queryset keeps the query count where it is. This is what the code plainly
   meant to do.
2. **Drop the field.** If a per-label photo is not actually wanted, remove ``photo`` from
   ``Label`` and the ``photo_id`` from the ``bulk_create``, and make the chevrons set the
   species photo instead -- which is the control issue 037 observes is missing.

Either way the fix wants a test that POSTs a photo choice and asserts the following GET
returns it; there is none today, which is why this survived eight years.

Related: issue 037 (nothing in the UI explains any of this), issue 010 (the same ``post``
pairs submitted items to new labels by position), issue 017 (the Vue editor has no
browser test, so only the JSON contract is covered).

Resolution
==========

Commit c9cb3f5, together with issue 010 -- the same handler. The read path now
hands the label down instead of one flag off it::

    photo_pk, photo_alternatives = get_species_photo_info(
        species, photo_pks_and_urls_by_title,
        photo=label.photo if label else None)

and ``get_species_photo_info`` prefers that photo over ``species.photo``
(``selected_photo = photo or species.photo``), so the species photo is what a
label without a choice of its own falls back to, and what a species with no
``Label`` row still gets -- ``get_labels_data`` passes ``None`` on that branch,
which also carries the ``visible=True`` it used to pass literally. The photo is
still offered among ``all_photos`` either way, so the chevrons can walk back to
the species photo.

The label queryset gained ``photo``::

    Label.objects.select_related('species', 'photo').order_by('species__name_fi')

Query count for the GET, measured in
``test_labels_api_get_reads_the_label_photo_without_more_queries`` -- three
species, two of them labelled with a photo of their own:

* before the change: 18
* after the change: 16

It cannot grow: ``select_related`` widens the ``Label`` query rather than adding
one. It shrinks because a label with a photo of its own never touches
``species.photo``, and the label queryset follows ``species`` but not
``species__photo``, so reading that used to cost a query per label.

Four tests were added, all of which fail against the old code except where noted:
``test_labels_api_get_reads_back_the_label_photo`` (the label's photo wins over
the species photo, both still offered),
``test_labels_api_get_falls_back_to_the_species_photo`` (a species with no label
and a label with no photo; passes before and after, as it must),
``test_labels_api_post_round_trips_the_photo_choice`` (the round trip this issue
asked for) and the query-count test above. In each, two photos match the species
by title and the one the species points at is the one saved last, since
``autoconnect_photo_to_species`` attaches on every save -- so the species photo
is a real alternative to the label's, not an absence.

The ``display_size`` fixture moved from ``test_photos_integration.py`` to
``kasvimuseo/tests/conftest.py``: the view tests need photos whose
``get_display_url()`` works too, and it is the ``PhotoSizeCache`` reset around it
that makes that possible.
