=====================================================================
Issue 010: Labels API pairs submitted items to new labels by position
=====================================================================

:Status: Fixed
:Severity: Medium
:Area: views / labels API
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_views.py::test_labels_api_post_links_each_planting_to_its_own_species_label
:Depends on: (none)
:Blocks: (none)
:Related: 039 -- the same ``post`` handler
    017 -- neither is covered by a browser test
:Decision: Option 1, create the labels one at a time and keep the mapping
    explicit. Option 2 -- key the mapping on ``species_id`` -- would reintroduce
    the same class of defect for two items naming the same species, since two
    items differ in the plantings they name and not in their species, so keying
    on the species would collapse them; an explicit mapping cannot. The label
    count is one per species on a print run, so the individual inserts cost
    nothing that matters. The delete-and-recreate is now wrapped in
    ``django.db.transaction.commit_on_success`` (Django 1.5's name for it), so
    the "failure part way through leaves the table empty" note below is fixed
    too, not deferred. Corrects one claim in the problem statement: the
    duplicate-species case does *not* break the old code on PostgreSQL --
    measured, it still pairs correctly, because the new primary keys come back
    in insert order there. The fragility is real, the failure was latent.
:Resolution: Fixed in c9cb3f5.

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

Resolution
==========

Commit c9cb3f5, together with issue 039 -- the same handler. The labels are
created one at a time and mapped as they are created, so nothing about the
mapping depends on how the database hands the rows back::

    @transaction.commit_on_success
    def post(self, request, *args, **kwargs):
        items = json.loads(request.body)
        Label.objects.all().delete()
        labels_by_external_id = {}
        for item in items:
            label = Label.objects.create(species_id=item['id'],
                                         photo_id=item['photo_pk'],
                                         visible=item['visible'])
            for external_id in item['external_ids']:
                labels_by_external_id[external_id] = label

The ``bulk_create`` is gone, and with it the ``Label.objects.order_by('pk')``
re-read: the labels a print run writes are one per species, so the individual
inserts are not a cost worth an assumption.

``commit_on_success`` covers the whole delete-and-recreate, including the
re-linking of the plantings, so the empty table this issue's last note describes
can no longer be left behind. Django 1.5 has no ``atomic``; ``commit_on_success``
is what it offers, and it commits or rolls back for real only outside a test's
own transaction -- Django 1.5's ``TestCase`` replaces ``transaction.rollback``
with a no-op, so
``test_labels_api_post_keeps_the_old_labels_when_the_save_fails`` is marked
``django_db(transaction=True)``. It monkeypatches ``Planting.save`` to raise
after the labels are written and asserts the label that was there before is the
one still there, by primary key.

What was measured, running the tests against the old handler:

* The extended
  ``test_labels_api_post_links_each_planting_to_its_own_species_label`` -- two
  items naming the same species, each naming a different planting -- **passes**
  against the old code on PostgreSQL as well. The positional pairing survives it,
  because ``bulk_create`` inserts in input order there and the new primary keys
  sort the same way. So this issue's claim that duplicate species "breaks it
  outright" is wrong for PostgreSQL; the assertion is a contract, not a
  reproduction. It does discriminate between the two options above: keying the
  mapping on ``species_id`` fails it.
* The mid-save failure test fails against the old code, as it should: the table
  is left holding the new label rather than the old one.
