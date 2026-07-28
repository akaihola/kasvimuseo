=======================================================================
Issue 003: Photo-to-species matching is case-sensitive and inconsistent
=======================================================================

:Status: Open
:Severity: Medium
:Area: models / photos
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_signals.py, kasvimuseo/tests/test_photos_integration.py
:Decision: undecided
:Resolution: (none yet)

Problem
=======

Two places match photos to species by the first word of the photo title, and they do
not agree.

``autoconnect_photo_to_species`` lowercases the title word but then compares it against
``name_fi`` exactly, so a species whose ``name_fi`` is capitalised can never be
auto-attached.

``photos.get_species_photos`` goes the other way -- it looks up
``species.name_fi.split()[0]`` **without** lowercasing, against dictionary keys that were
lowercased from the photo titles. It also raises ``IndexError`` if ``name_fi`` is blank.

Impact
======

Photos silently fail to attach, or fail to appear on the species report, depending on capitalisation of data the user typed.

Options
=======

Normalise on one side only, in one helper used by both call sites -- lowercase both
the title word and ``name_fi``, and treat a blank ``name_fi`` as "no match" rather than
letting ``split()[0]`` raise.
