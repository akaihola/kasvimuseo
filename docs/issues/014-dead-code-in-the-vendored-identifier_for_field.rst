=========================================================
Issue 014: Dead code in the vendored identifier_for_field
=========================================================

:Status: Open
:Severity: Low
:Area: templatetags / vendored
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_admin_changelist.py (covers the reachable branches)
:Depends on: 034 -- ruled: the fork is retired, so this file goes with it and
    there is nothing to fix
:Blocks: (none)
:Related: 034 -- the same vendored file
:Decision: Do neither option. 034 ruled the whole fork retired, with the
    deletion scheduled for upgrade Stage 5 (Django 1.7, where Django's own
    ``field-``/``column-`` classes make it redundant), so ``identifier_for_field``
    has a deletion date and its dead branch is not worth repairing on the way
    there. Two of the three Django API removals nobody had listed --
    ``_meta.module_name`` at 1.8 and ``_meta.get_field_by_name`` at 1.10 -- are
    in this same function, which is a second reason not to invest in it.
:Resolution: (none yet -- closes when the file is deleted in Stage 5)

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

Settled by 034
==============

That last sentence turned out to be the whole answer. Django closed ticket
11195 itself in **1.7**, so the fork stops being a customisation at upgrade
Stage 5, and 034 ruled it deleted there rather than carried. Neither option
above is taken: the dead branch stays exactly as it is until the file goes.

``Status`` stays ``Open`` because the file is still in the tree. It becomes
``Fixed`` -- by deletion -- in the Stage 5 commit, and the four steps of that
deletion are listed under Stage 5 in ``docs/upgrade-plan.rst``. Nothing here
should be worked on before then; picking this up would mean repairing code with
a deletion date.
