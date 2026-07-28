=========================================================
Issue 014: Dead code in the vendored identifier_for_field
=========================================================

:Status: Open
:Severity: Low
:Area: templatetags / vendored
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_admin_changelist.py (covers the reachable branches)
:Depends on: 034 -- if the fork is retired, this file goes with it and there is nothing to fix
:Blocks: (none)
:Related: 034 -- the same vendored file
:Decision: undecided
:Resolution: (none yet)

Problem
=======

In ``kasvimuseo/templatetags/kasvimuseo_admin_list.py``, ``identifier_for_field``
assigns a label it never returns::

    if hasattr(attr, "name"):
        label = attr.name
    elif callable(attr):
        ...
    return '__unknown__'

When the resolved attribute has a ``.name``, the function falls through to
``'__unknown__'``, so the assignment is dead. For every ``list_display`` entry this
project uses, the final ``return`` is unreachable.

Impact
======

None observed -- no current column takes that branch. It is a trap for anyone adding a list_display entry that does.

Options
=======

1. Return ``label`` in that branch, if that was the intent.
2. Delete the dead assignment.

This file is a vendored fork of Django's own ``admin_list`` carrying the patch from
Django ticket 11195, so weigh any change against the cost of diverging further.
