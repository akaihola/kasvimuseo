==============================================================================
Issue 072: Deleting a photo deletes the plant species
==============================================================================

:Status: Open
:Severity: High
:Area: models / data safety
:Reported: 2026-08-17
:Source: Upgrade plan Stage 7, which added ``on_delete`` to every
    ``ForeignKey`` two Django versions before 2.0 requires it. Writing the rule
    down is what made it readable. Stage 7 wrote ``CASCADE`` everywhere, because
    ``CASCADE`` is the default Django 1.x applied and an upgrade stage must not
    change behaviour, and it recorded that three of the twelve deserve a second
    look. This is that second look
:Evidence: (no test) -- no test in ``kasvimuseo/tests/`` deletes a
    ``photologue.Photo``, so nothing pins today's behaviour and nothing would
    fail if it changed. That absence is part of the finding: the fix should
    arrive with a test that deletes a photo and asserts the species survives.
    What is readable today is the declaration.
    ``kasvimuseo/models.py`` gives ``Species.photo`` and ``Label.photo``
    ``null=True, blank=True, on_delete=models.CASCADE``, and ``Bed.plot`` the
    same three, and ``kasvimuseo/migrations/0001_initial.py`` says the same
:Depends on: (none) -- the ``on_delete`` arguments are in the tree since Stage 7
:Blocks: (none)
:Related: 036, the upgrade programme, whose Stage 7 section states the three
    fields and defers the ruling to here. Also ``Planting.label``, in the same
    model file, which is the precedent: it is the one nullable foreign key that
    already says ``SET_NULL``, and nobody wrote down why it differs
:Decision: undecided
:Resolution: (none yet) -- the three fields are declared ``CASCADE`` in the tree
    and stay that way until the ``Decision`` field above is filled in

What happens
============

An editor opens the photologue admin and deletes a photo. Django follows
``Species.photo`` and deletes **the plant species that showed it**. Then it
follows the foreign keys behind that species and deletes its ``Observation``
rows, and behind those the ``Planting`` rows, and behind those the ``Care``
rows and ``PlantingPhoto`` rows. One deleted image removes a plant's whole
record from the museum.

``Label.photo`` does the same to labels. ``Bed.plot`` deletes a bed when its
plot goes, which is arguable rather than clearly wrong, and is listed here so
the ruling covers all three nullable fields at once.

Django's admin shows a confirmation page listing what it is about to delete, so
this is not silent. It is still a delete an editor has no reason to expect, on
a page about photographs.

Why the field is nullable and cascading at the same time
========================================================

Nothing chose it. Django 1.x let a ``ForeignKey`` omit ``on_delete`` and
applied ``CASCADE``, so twelve fields in this project inherited a delete rule
nobody typed. ``null=True`` says the application already handles a species with
no photo, which is exactly the state ``SET_NULL`` would produce.

So the two declarations disagree: ``null=True`` says "this may be empty", and
``CASCADE`` says "if it empties, delete the row". ``SET_NULL`` is what the rest
of the declaration asks for.

What to change, if the ruling agrees
====================================

Three fields in ``kasvimuseo/models.py``, and the matching three entries in
``kasvimuseo/migrations/0001_initial.py``:

============================ ================= ====================
Field                        Today             Proposed
============================ ================= ====================
``Species.photo``            ``CASCADE``       ``SET_NULL``
``Label.photo``              ``CASCADE``       ``SET_NULL``
``Bed.plot``                 ``CASCADE``       ``SET_NULL``
============================ ================= ====================

Three things the fix has to carry:

#. **A test for each field.** Delete the photo, assert the species is still
   there and its ``photo`` is ``None``. Today's behaviour is pinned by nothing,
   which is why this issue could exist for thirteen years unnoticed.
#. **No migration, probably.** ``on_delete`` never reaches the schema, and
   Stage 7 measured that changing it on the model produces no migration:
   Django's autodetector compares deconstructed fields, and the historical
   field and the model field deconstruct alike once both name a rule. Check with
   ``makemigrations kasvimuseo --dry-run`` rather than assume, and edit
   ``0001_initial.py`` in the same commit so the two agree.
#. **A note on ``Planting.label``.** It already says ``SET_NULL`` and no comment
   says why. Whoever fixes this should write one sentence there, so the next
   reader sees a rule rather than an exception.

Why this is not part of Stage 7
===============================

A framework bump that also changes what a delete does is two changes wearing one
commit. Stage 7's whole argument is that one thing moves at a time, so the suite
can say which thing broke. ``CASCADE`` preserved the behaviour and this file
carries the question, which is the split the upgrade plan asks for.

The urgency is also lower than the severity suggests, and worth stating plainly
so nobody rushes it. ``CASCADE`` has been the rule since these models were
written in 2013, so this is a thirteen-year-old defect rather than a regression
Stage 7 introduced. What Stage 7 changed is that the rule is now written down
where a reader can see it.
