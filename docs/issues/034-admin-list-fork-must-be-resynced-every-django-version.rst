==========================================================================
Issue 034: The admin_list fork has to be re-synced at every Django version
==========================================================================

:Status: Open
:Severity: High
:Area: templatetags / vendored / Django upgrade
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: kasvimuseo/tests/test_templatetags.py (pins the current output)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``kasvimuseo/templatetags/kasvimuseo_admin_list.py`` is a copy-and-modify fork
of Django's own ``django/contrib/admin/templatetags/admin_list.py``. It
reimplements ``result_headers``, ``items_for_result`` and ``results``, and
reaches into six private admin symbols to do it::

    from django.contrib.admin.templatetags.admin_list import (
        result_hidden_fields, result_headers, ResultList)
    from django.contrib.admin.util import (
        lookup_field, display_for_field, display_for_value, label_for_field)
    from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE, ORDER_VAR

Django changes these between releases. Two of the six break within the first
few upgrade stages: ``django.contrib.admin.util`` is renamed to ``.utils`` and
the old name is deleted in **1.9**, and ``EMPTY_CHANGELIST_VALUE`` is removed
in the same release, replaced by ``ModelAdmin.empty_value_display``.

The upgrade crosses **19 Django versions**. This file has to be re-checked
against Django's current copy at each one, and it is 235 lines of code whose
behaviour is only pinned by the admin changelist rendering tests.

Its actual purpose is small: putting the field name into each ``<td class=...>``
so the CSS can target columns.

Impact
======

Plausibly the single largest recurring cost in the whole upgrade -- more than
all the other code changes combined, because it recurs at every stage rather
than once. It is also the piece most likely to fail silently, since a
changelist that renders with slightly wrong markup still renders.

Options
=======

1. **Retire it.** Produce the same ``<td>`` classes with ``list_display``
   callables returning ``format_html``-wrapped markup, which needs no private
   API at all, or with CSS targeting ``nth-child`` via ``ModelAdmin.Media``.
   This ends the recurring cost permanently.
2. **Re-derive it once at the end.** Keep the fork, but rather than porting it
   nineteen times, freeze the admin changelist customisation until the Django
   upgrade is complete and then re-fork from Django 6.0's source in one step.
   Cheaper than option 1 up front, but leaves the coupling in place.
3. Carry it stage by stage, as the plan currently assumes.

**Decide this before Stage 6**, not after -- that is the last point where the
choice is still cheap.

See also
========

Issue 014 covers dead code inside the same file. ``docs/upgrade-plan.rst``
Part 6, "The admin-list fork is the real cost".
