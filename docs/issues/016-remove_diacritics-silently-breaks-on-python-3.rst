========================================================
Issue 016: remove_diacritics silently breaks on Python 3
========================================================

:Status: Fixed
:Severity: Medium
:Area: forms / Python 3 migration
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_forms.py --
    ``test_remove_diacritics_returns_a_text_string`` pinned the Python 2
    behaviour before the fix and now pins the fixed one, over an accented, an
    unaccented and an empty string; ``test_a_saved_photo_gets_an_accent_free_slug``
    was added with the fix and takes an accented title through ``PhotoForm``
    to the saved ``Photo``'s ``title_slug``
:Depends on: (none)
:Blocks: 036 -- silent slug corruption at Stage 10, the Python 3 flip
:Related: 024 -- the other Python 3 landmine already on file
:Decision: Take the option below -- ``u''.join(character for character in
    normalize('NFKD', text) if not combining(character))`` -- and take it now,
    rather than as part of Stage 10. On Python 2 it returns exactly what
    ``filter()`` returned: the same characters in the same order, and a
    ``unicode`` either way, so no slug this database already holds changes and
    nothing has to be migrated. It needed no ruling, since the choice is
    between a construct that is correct on one interpreter and one that is
    correct on both.
:Resolution: 4a9881a -- the join in ``kasvimuseo/forms.py``, the widened pin
    and the new end-to-end slug test in ``kasvimuseo/tests/test_forms.py``

Problem
=======

``kasvimuseo/forms.py`` stripped accents with::

    remove_diacritics = lambda u: filter(lambda x: not combining(x), normalize('NFKD', u))

On Python 2 ``filter`` over a string returns a string. On Python 3 it returns an iterator,
which ``slugify`` would stringify into something like ``<filter object at 0x...>``.

The failure is silent -- no exception, just a mangled ``title_slug`` on every photo whose
title was auto-derived. A test asserts the result is a text string, so the migration
fails loudly instead.

Impact
======

On a Python 3 migration, photo slugs would be corrupted without any error.

Options
=======

Replace with ``u''.join(...)`` over the same comprehension, which behaves identically
on both versions. Safe to do now, before any migration.

Decision
========

That option, taken now rather than at Stage 10. There was nothing to rule
between: one construct is correct on one interpreter, the other on both.

Python 2 behaviour is unchanged, which is the part worth stating. ``filter()``
over a ``unicode`` string built its result by keeping the characters the
predicate accepted, in order, and returning a ``unicode``; ``u''.join()`` over
the same predicate keeps the same characters in the same order and returns a
``unicode`` too. So every ``title_slug`` this database already holds is the
slug the fixed code would produce, and no migration or re-save is needed.

Doing it before the flip rather than during it also keeps it out of Stage 10's
diff, which is large enough without a change that can be made and tested
against the running interpreter.

Resolution
==========

``remove_diacritics`` in ``kasvimuseo/forms.py`` is now::

    return u''.join(character for character in normalize('NFKD', text)
                    if not combining(character))

and the comment above it no longer describes an outstanding bug.

``kasvimuseo/tests/test_forms.py`` gains two things. The existing pin,
``test_remove_diacritics_returns_a_text_string``, is parametrised over an
accented string, an unaccented one -- which has to come back unchanged, not
merely be of the right type -- and the empty string. And
``test_a_saved_photo_gets_an_accent_free_slug`` exercises the path this issue
is actually about end to end: an accented title through ``PhotoForm``, saved,
and the ``title_slug`` read back off the ``Photo``.

What was run where: the suite, 387 tests, on Python 2.7 in the application
container. Python 3 was **not** exercised against this project -- nothing on
the host has Django 1.5 -- but the expression itself needs only
``unicodedata``, and it was run standalone under the host's Python 3.14 over
the same three inputs, returning ``str`` each time and
``'Kevatesikko ahkyssa'`` for the accented one.

Commit 4a9881a.
