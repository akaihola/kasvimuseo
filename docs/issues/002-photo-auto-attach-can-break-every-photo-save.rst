=======================================================
Issue 002: Photo auto-attach can break every Photo save
=======================================================

:Status: Open
:Severity: High
:Area: models / admin
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_signals.py
:Depends on: (none)
:Blocks: 042 -- dropping ``photo__isnull=True`` widens this same fault
    037 -- the instructions asked for there describe this receiver
:Related: 003, 042 -- the same auto-attach receiver
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``autoconnect_photo_to_species`` is a ``post_save`` receiver connected for **every**
model. It looks the matching species up with::

    species = Species.objects.get(name_fi=species_name, photo__isnull=True)

and catches only ``Species.DoesNotExist``. ``Species.name_fi`` has no unique constraint,
so as soon as two photoless species share a Finnish name, the lookup raises
``MultipleObjectsReturned`` -- from a receiver that runs on every save.

Impact
======

Saving any Photo, including through the admin, raises. The receiver is global, so the blast radius is larger than the photo feature itself.

Options
=======

1. Catch ``MultipleObjectsReturned`` as well and skip the auto-attach.
2. Use ``.filter(...)[:1]`` and attach to the first match.
3. Add a unique constraint on ``name_fi`` -- bigger change, and the data may not allow it.

Whichever is chosen, keep the receiver total: it runs on every save in the project.
