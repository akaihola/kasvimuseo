=======================================================
Issue 002: Photo auto-attach can break every Photo save
=======================================================

:Status: Fixed
:Severity: High
:Area: models / admin
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_signals.py
:Depends on: (none)
:Blocks: 042 -- dropping ``photo__isnull=True`` widens this same fault
    037 -- the instructions asked for there describe this receiver
:Related: 003, 042 -- the same auto-attach receiver
:Decision: Option 1 -- catch ``MultipleObjectsReturned`` and skip the
    auto-attach. It is the only option that cannot silently attach a photo to
    the wrong species, and it needs no migration. Option 3 was not taken: a
    unique constraint on ``name_fi`` wants a data migration and a look at the
    production data, neither of which this change can do. The connection was
    narrowed to ``sender=Photo`` in the same change; the existing ``sender !=
    Photo`` guard already made that a no-op for every other model, so it
    changes no behaviour, and the guard was kept.
:Resolution: 6089276

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

Fix
===

Option 1. ``autoconnect_photo_to_species`` now catches
``Species.MultipleObjectsReturned`` alongside ``Species.DoesNotExist``, so an
ambiguous name skips the auto-attach instead of failing the ``Photo`` save.
Nothing is attached in that case, and nothing tells the user so -- the photo
still has to be pointed at a species by hand, which is 042's and 037's
territory rather than this issue's.

The receiver is also connected for ``sender=Photo`` alone now, rather than for
every model. Its own ``sender != Photo`` guard already made every other sender
a no-op, so this changes no behaviour; it only stops the receiver being invoked
on saves it has nothing to do with. The guard is kept, and
``kasvimuseo/tests/test_signals.py`` pins it by calling the receiver directly.

Option 3 stays available: a unique constraint on ``name_fi`` would remove the
ambiguity at the source, but it needs a data migration and a look at the
production data to know whether the existing rows allow it.
