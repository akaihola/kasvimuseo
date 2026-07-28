========================================================
Issue 016: remove_diacritics silently breaks on Python 3
========================================================

:Status: Open
:Severity: Medium
:Area: forms / Python 3 migration
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_forms.py::test_remove_diacritics_returns_a_text_string
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``kasvimuseo/forms.py`` strips accents with::

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
