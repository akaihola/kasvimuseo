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
:Decision: Option 1, then refined: catch ``MultipleObjectsReturned``, try to
    narrow the namesakes down to one on the evidence in the garden records and
    in the photo's file name, and skip the auto-attach only when nothing
    separates them. Option 1 was chosen over option 2 because attaching to
    whichever row came back first is a guess dressed as an answer; the
    refinement is the maintainer's, and it buys the attach that option 2 would
    have made blindly, at the price of having to be right. Option 3 was not
    taken: a unique constraint on ``name_fi`` wants a data migration and a look
    at the production data, neither of which this change can do. The connection
    was narrowed to ``sender=Photo`` in the same change; the existing ``sender
    != Photo`` guard already made that a no-op for every other model, so it
    changes no behaviour, and the guard was kept.
:Resolution: 6bbd199, refined in 96fe07d

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

Option 1. ``autoconnect_photo_to_species`` no longer lets an ambiguous name out
of ``post_save``: ``Species.DoesNotExist`` and ``Species.MultipleObjectsReturned``
are both handled, so the ``Photo`` save completes either way.

The receiver is also connected for ``sender=Photo`` alone now, rather than for
every model. Its own ``sender != Photo`` guard already made every other sender
a no-op, so this changes no behaviour; it only stops the receiver being invoked
on saves it has nothing to do with. The guard is kept, and
``kasvimuseo/tests/test_signals.py`` pins it by calling the receiver directly.

Telling the namesakes apart
---------------------------

Skipping the auto-attach was the first fix and is still what happens when
nothing distinguishes the candidates. Before it gives up, the receiver now asks
``kasvimuseo/photo_matching.py`` which of the namesakes the photo belongs to.

Three filters, in order, each skipped rather than applied when it would leave
nothing -- absent evidence is not evidence against:

1. the species has been observed at all;
2. one of those observations has a planting with no removal date;
3. the species has labels.

Then three rankings, the first that separates the field deciding:

4. whose living plantings were cared for most recently;
5. whose own names -- and the names of the places its observations came from,
   and the nicknames they go by -- best match the photo's **file name**. The
   title chooses the species, as it always has; the file name is what tells
   namesakes apart, and the two are not always written the same way;
6. which of them has no photo yet. Added with 042, which is what made a
   species that already has a photo a candidate at all.

Similarity is ``difflib`` on accent-stripped, case-folded words, scored by
corroboration: a field counts only if it clears ``MATCH_THRESHOLD``, and a
candidate's score is the *sum* of the fields that do, so a file name naming
both the plant and the house it came from beats one that only repeats the
Finnish name both candidates share. The winner must beat the runner-up by
``WINNING_MARGIN``; anything less conclusive returns nothing and the photo
stays unattached.

Two things this deliberately does not do. It does not tell the user what
happened, either way -- an unattached photo still has to be pointed at a
species by hand, which is 042's and 037's territory rather than this issue's.
And step 5 rests on photographs being named after what is in them; where they
are named ``IMG_4021.jpg`` it can never fire, and the whole benefit is steps 1
to 4.

It is worth being plain about the trade: where the old code did nothing, this
can now attach a photo to the wrong species. The two thresholds are what bound
that, and they are module constants so they can be tuned without reading the
algorithm.

What the production data says
-----------------------------

Checked against a restored copy while fixing 042, which is the change that made
this fault reachable in the first place: 156 species, 113 with a photo, and
exactly **one** duplicated ``name_fi`` -- two ``tarhakurjenmiekka``, both of
which already have photos.

Two things follow. While ``photo__isnull=True`` was in the lookup this crash
could not actually happen in production, because the only two candidates it
needs were filtered out before the lookup ran; it was a latent fault, waiting
for either a second photoless namesake or for 042. And the disambiguation is
not decoration: since 042 those two are ambiguous on every photo titled after
them, and it is what tells them apart -- correctly, on their real names, which
``test_signals.py`` now has a test for.

**Option 3 is not applicable to this data as it stands.** A unique constraint on
``name_fi`` would need the two ``tarhakurjenmiekka`` -- genuinely different
plants, ``Iris x`` and ``Iris 'Cracchus'`` -- renamed or merged first. That is a
decision about the collection rather than about the code, and it is the reason
this was not the fix.
