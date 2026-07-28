=================================================================
Issue 039: The label photo is saved but never read back
=================================================================

:Status: Open
:Severity: Medium
:Area: views / labels API
:Reported: 2026-07-28
:Source: Walkthrough of how photo management is meant to be used
:Evidence: (none -- no test round-trips a photo choice through the API)
:Depends on: (none)
:Blocks: 037 -- option 3 there depends on what this decides
:Related: 010 -- the same ``post`` handler
    042 -- the control that looks like it should set the species photo
    017 -- the Vue editor has no browser test
:Decision: undecided
:Resolution: (none yet)

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
