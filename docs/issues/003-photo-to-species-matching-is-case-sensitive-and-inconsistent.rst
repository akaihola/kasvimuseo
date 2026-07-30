=======================================================================
Issue 003: Photo-to-species matching is case-sensitive and inconsistent
=======================================================================

:Status: Fixed
:Severity: Medium
:Area: models / photos
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_signals.py, kasvimuseo/tests/test_photos_integration.py
:Depends on: (none)
:Blocks: 037 -- the filename convention documented there is this matching rule
:Related: 002, 042 -- the same auto-attach receiver
    043 -- the same file names, seen from the admin changelist
:Decision: One helper, ``photo_matching.match_key`` -- the first word, lower-cased,
    or ``None`` -- used by both call sites. Python folds the case it can, and the
    one comparison that has to happen in SQL says ``name_fi__iexact`` rather than
    leaning on a collation; both are argued in "Decision" below.
:Resolution: Fixed in 3da66c3.

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

Decision
========

**The shared thing is a normalisation function, not a lookup.** The two call
sites work at different levels -- the receiver matches one title against the
database, the species report pairs many species against a dictionary keyed by
title word -- so nothing they could both call would do the lookup for them.
What they can share is the rule itself, and that is one line of it::

    def match_key(text):
        if not text:
            return None
        words = text.split()
        return words[0].lower() if words else None

It lives in ``kasvimuseo.photo_matching``, which is already the module about
matching photos to species, is already imported by ``kasvimuseo.models``, and
imports neither of its callers. ``kasvimuseo.photos`` now imports it too.
``None`` rather than ``''`` for "no word in it": ``dict.get(None)`` is a miss,
which is exactly the answer wanted for a blank ``name_fi``, and the receiver
tests it explicitly before touching the database. Both former ``split()[0]``
sites go through it, so neither can raise ``IndexError`` again, and there is one
convention rather than three.

**The folding is Python's, except for the one comparison that must be SQL.**
``get_species_photos`` and ``get_photo_titles_pks_and_urls`` compare two Python
strings and both get their keys from ``match_key``, so they agree by
construction. The receiver cannot: it needs a *queryset* -- ``disambiguate``
filters and aggregates over it -- so the species side of its comparison is a
column, and no amount of Python lowercasing reaches it. Lowercasing in Python
there would mean loading every species on every photo save, so the lookup is
``name_fi__iexact=species_name``.

That is consistent with issue 043, which left the photo changelist's *ordering*
to the database's collation, and for the reason 043 gives: no PostgreSQL
collation folds case for equality -- ``'Kuva' = 'kuva'`` is false under
``en_US.UTF-8`` as much as under ``C`` -- so a comparison that must ignore case
has to say so itself. ``iexact`` is saying so; it is not the collation deciding.
The two clusters therefore cannot diverge here the way 043 documents them
diverging for sort order.

**What was deliberately left alone.** The receiver matches the title word
against the whole of ``name_fi``, while the report matches it against
``name_fi``'s first word, so a two-word ``name_fi`` is still reachable from the
report and not from the receiver. That difference is not about case, it predates
this issue, and narrowing it either way changes which photos attach in
production -- so it stays as it is rather than being decided in passing here.

While proving the case-folding on real rows, ``get_photo_pks_and_urls_by_species``
turned out to drop photos: it grouped with ``itertools.groupby`` over rows in
*title* order, and once the key is case-folded two photos sharing a key need not
be adjacent, so ``Valkonarsissi kukassa`` and ``valkonarsissi lehdet`` produced
two groups of which the dictionary kept only the last. It accumulates into a
dictionary instead. The fix for the case-sensitivity is what would have exposed
this, so it is fixed here rather than filed.
