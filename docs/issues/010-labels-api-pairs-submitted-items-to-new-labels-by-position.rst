=====================================================================
Issue 010: Labels API pairs submitted items to new labels by position
=====================================================================

:Status: Open
:Severity: Medium
:Area: views / labels API
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_views.py::test_labels_api_post_links_each_planting_to_its_own_species_label
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``PlantedSpeciesLabelsApi.post`` deletes every ``Label``, bulk-creates replacements, and
then pairs the submitted items back to the created rows **by position**::

    Label.objects.bulk_create([...])
    labels = Label.objects.order_by('pk')
    external_ids = {external_id: label
                    for item, label in zip(items, labels) ...}

This assumes ``bulk_create`` inserts in input order and that the new primary keys sort the
same way. On PostgreSQL that currently holds -- it was tested with several items, holes in
the pk sequence and descending input order, and each planting landed on its own species'
label.

It is still fragile: it breaks if ``items`` ever contains two entries for the same species,
and it is not a guarantee the database API makes.

Impact
======

If the assumption ever fails, every planting label silently points at the wrong species. The failure is silent -- nothing raises.

Options
=======

1. Create the labels one at a time and keep the mapping explicit, trading a bulk insert
   for correctness that does not depend on insert ordering.
2. Key the mapping on ``species_id``, which is present in each item, instead of position.

Note the handler also deletes all labels before recreating them, so a failure part way
through leaves the table empty.
