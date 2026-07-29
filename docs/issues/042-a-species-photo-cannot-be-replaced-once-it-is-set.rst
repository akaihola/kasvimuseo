============================================================
Issue 042: A species photo cannot be replaced once it is set
============================================================

:Status: Fixed
:Severity: Medium
:Area: models / photos
:Reported: 2026-07-28
:Source: Implementation plan on branch ``species-photo-always-switch``
:Evidence: kasvimuseo/tests/test_signals.py --
    ``test_photo_does_not_overwrite_an_existing_species_photo`` pinned the
    defect and was inverted by the fix
:Depends on: 002 -- the ``MultipleObjectsReturned`` risk this change widens
:Blocks: 037 -- the capability the missing instructions would describe
:Related: 003 -- the same auto-attach receiver
    039 -- the control that looks like it should do this
:Decision: Drop the ``photo__isnull=True`` filter, so the photo saved last
    wins. Ruled on when the defect was reported from the garden a second time,
    as a photo that would not change; the admin control is not excluded and can
    still follow.
:Resolution: 942532c

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

Fix
===

The filter is gone; the photo saved last wins. Both consequences the options
above asked to be designed around were checked against a restored copy of the
production database rather than guessed at.

**The duplicate names.** The check the options section asks for gives 156
species, 113 of them with a photo, and exactly **one** duplicated ``name_fi``:
two ``tarhakurjenmiekka``, *both of which already have photos*. So the
``MultipleObjectsReturned`` of issue 002 was not reachable in production while
``photo__isnull=True`` was there -- both duplicates were filtered out before
the lookup ran -- and dropping the filter is exactly what makes it reachable.
That is what the dependency on 002 was about, and it was the right way round.

Those two are now a live case rather than a hypothetical one, and 002's
disambiguation handles them: both of their existing photographs are named after
the house they were taken at (``Tarhakurjenmiekka.Kurala.182.jpg`` and
``Tarhakurjenmiekka 'Cracchus.Peltomäki.178.jpg``), and each house is the origin
of that species' observations. ``test_signals.py`` carries a test built from
their real names.

One tie-break was added to ``photo_matching`` for this change: when nothing else
separates two namesakes, prefer the one that has no photo yet. It is the better
guess, and it preserves the pre-042 behaviour in the case that used to be the
only one this receiver could reach.

**Every save re-attaches.** This is accepted rather than designed around, as the
options section allows. Correcting a title in the admin pulls the species photo
back to that photo; the workflow is "save the one you want last". That sentence
belongs in the instructions issue 037 asks for.

The same check settles 002's option 3 as well, from the other end: a unique
constraint on ``name_fi`` is **not** applicable to this data as it stands. The
two ``tarhakurjenmiekka`` are genuinely different plants -- ``Iris x`` and
``Iris 'Cracchus'`` -- so the constraint would need them renamed or merged
first, which is a decision about the collection rather than about the code.

A second cause, found by reproducing the report
-----------------------------------------------

Dropping the filter was not enough to make the reported upload work, and the
reason had nothing to do with this issue. ``PhotoForm.clean()`` overrode
``clean()`` without calling ``super()``, and ``BaseModelForm.clean()`` is the
only thing that sets the flag making ``_post_clean()`` run
``validate_unique()``. So the form checked no uniqueness at all, and
``Photo.title`` and ``Photo.title_slug`` are both unique: **re-uploading a
photo under a title already in use returned a 500** from PostgreSQL's
constraint, with the image file already written to ``MEDIA_ROOT`` and no row
pointing at it.

That is why the report arrived twice. The first upload created the photo and
did not attach it, which is this issue. Every later attempt with the same title
failed before it got as far as attaching anything, which is not -- and left an
orphan ``..._1.JPG`` next to the original as its fingerprint.

Fixed in the same change, with tests in ``kasvimuseo/tests/test_forms.py``: a
duplicate title is now an error on the form. It still does not let two photos
share a title, because photologue does not allow that; the way to replace a
photo whose title is already right is to re-save the existing one, which now
attaches it.

Not done here: the admin control. Adding ``photo`` to ``SpeciesAdmin.fieldsets``
is still worth doing and is still not exclusive with this, but it does not help
whoever is standing in the garden with a phone, which is where the photographs
come from and where this was reported from.

Notes
=====

Filed from ``PLAN-species-photo-always-switch.md``, written on branch
``species-photo-always-switch`` and kept out of the repository until now. The
branch is merged, and the change it plans is now implemented -- see ``Fix``
above; what took the time was not the one line but its second consequence,
which is issue 002.

Read with 002 and 003, which concern the same receiver, 037 for the instructions
that depend on this behaviour, and 039 for the control that looks like it should
do this and does not.
