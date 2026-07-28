============================================================
Issue 042: A species photo cannot be replaced once it is set
============================================================

:Status: Open
:Severity: Medium
:Area: models / photos
:Reported: 2026-07-28
:Source: Implementation plan on branch ``species-photo-always-switch``
:Evidence: (none)
:Depends on: 002 -- the ``MultipleObjectsReturned`` risk this change widens
:Blocks: 037 -- the capability the missing instructions would describe
:Related: 003 -- the same auto-attach receiver
    039 -- the control that looks like it should do this
:Decision: undecided
:Resolution: (none yet)

Problem
=======

The photo shown for a species in the mobile plant list
(``/planted-species/``) comes from ``Species.photo``
(``kasvimuseo/templates/kasvimuseo/reports/planted-species-list.html``, line
24). There is no way to change it:

* ``SpeciesAdmin.fieldsets`` does not include ``photo``, so the admin form never
  offers it.
* ``PhotoAdmin``'s ``SpeciesInline`` shows only ``name_fi``.
* The photo picker on the label page writes ``Label.photo``, which is a
  different field -- and one nothing reads back (issue 039).

That leaves exactly one place where the field is ever set, the ``post_save``
receiver ``autoconnect_photo_to_species`` in ``kasvimuseo/models.py``::

    species = Species.objects.get(name_fi=species_name,
                                  photo__isnull=True)

``photo__isnull=True`` means the *first* matching photo wins permanently.
Uploading a better photo later does nothing at all. Changing the picture on a
species currently requires a Django shell on the production server.

Impact
======

The public species list is stuck with whatever photo happened to be uploaded
first, including a bad one. From the maintainer's point of view the interface
simply does not respond: the upload succeeds, the list does not change, and
nothing explains why. Issue 037 is about the missing instructions; this is the
missing capability behind them.

Options
=======

**Drop the ``photo__isnull=True`` filter**, so the most recently saved photo
wins. One line in ``kasvimuseo/models.py``, no migration::

        species = Species.objects.get(name_fi=species_name)

Two consequences to accept or design around before this is applied:

* **Every** ``Photo.save()`` re-attaches, not just an upload of a new file.
  Correcting a title in the admin would pull the species photo back to that
  photo. The workflow becomes "save the one you want last", which is worth
  writing down in the instructions asked for by issue 037.
* ``Species.objects.get()`` can raise ``MultipleObjectsReturned`` when two
  species share a ``name_fi``. The risk exists today but grows once
  ``photo__isnull=True`` no longer narrows the candidates; issue 002 is the same
  fault in its other form -- an exception here breaks *every* photo save.
  Check the production data first::

      Species.objects.values('name_fi').annotate(n=Count('id')).filter(n__gt=1)

  If there are duplicates, use ``filter()`` and a loop rather than ``get()``.

**Or give the field a control.** Adding ``photo`` to ``SpeciesAdmin.fieldsets``
makes the choice explicit and leaves the automatic first-attach alone. It is a
larger admin change, and it does not help whoever is working from a phone in the
garden, which is where the photos come from.

The two are not exclusive: the filter can go now and the admin field can follow.

Tests to add either way, in ``kasvimuseo/tests/test_photos.py``: a photo
attaches to a species that has none, a photo replaces an existing one, an empty
title does nothing, and an unknown species name does not raise.

Notes
=====

Filed from ``PLAN-species-photo-always-switch.md``, written on branch
``species-photo-always-switch`` and kept out of the repository until now. The
branch is merged; the change it plans is *not* implemented -- ``models.py`` still
carries the filter.

Read with 002 and 003, which concern the same receiver, 037 for the instructions
that depend on this behaviour, and 039 for the control that looks like it should
do this and does not.
