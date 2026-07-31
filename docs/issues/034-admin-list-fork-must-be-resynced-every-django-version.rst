==========================================================================
Issue 034: The admin_list fork has to be re-synced at every Django version
==========================================================================

:Status: Fixed
:Severity: High
:Area: templatetags / vendored / Django upgrade
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``kasvimuseo/tests/test_admin_changelist.py`` -- twelve tests use the
    ``fieldname_`` classes to address columns, and
    ``test_identifier_for_field_branches`` pins the fork's own function
:Depends on: (none)
:Blocks: 014 -- dead code in the same file, moot once the fork is deleted
    036 -- the largest recurring cost; decided before Stage 6, as asked
:Related: (none)
:Decision: **Retire it, at Stage 5.** Option 1 of the three below, with the
    deletion scheduled rather than done now: Django fixed this project's patch
    upstream in 1.7 (ticket #11195), so the stage that installs Django 1.7 is
    where the fork stops being needed and starts being a duplicate. No code
    changes today. The evidence is in "What was measured" below; the practical
    consequence is that ``kasvimuseo_admin_list.py``, its ``{% load %}`` and the
    ``fieldname_`` class names are deleted in Stage 5 and the five plan items
    that assumed the file would still exist at Stages 6, 7, 10 and 17 are gone.
:Resolution: Ruled and recorded in 508fd78; no code change. The deletion
    itself is Stage 5 work, listed there in ``docs/upgrade-plan.rst``.

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

What was measured
=================

The ruling above rests on four measurements rather than on the description in
"Problem", which was written from a reading of the imports.

The fork differs from Django only in the ``class`` attribute
-------------------------------------------------------------

A mechanical diff of ``result_headers``, ``items_for_result`` and ``results``
against the installed Django 1.5.1 copy is six hunks, ``-9 / +22`` lines.
``results`` is byte-identical. Every difference is a CSS class:

* the not-sortable header branch gains ``class="fieldname_X"``; stock yields no
  ``class_attrib`` at all, so the header renders with no class,
* the sortable branch's ``th_classes`` becomes ``['sortable', 'fieldname_X']``
  instead of ``['sortable']``,
* ``row_class`` -- a scalar each branch *overwrites* -- becomes ``row_classes``,
  a list seeded with ``fieldname_X`` to which ``action-checkbox`` and
  ``nowrap`` are *appended*.

Nothing else in the three functions differs: not the sort URLs, not the
``list_editable`` form handling, not the popup ``onclick``. The two additions
outside them are ``identifier_for_field`` (31 lines Django has no equivalent
of, at the time) and the renamed inclusion tag. The issue's claim that the
purpose is only the ``<td class=...>`` is therefore correct.

Almost none of the classes are consumed
---------------------------------------

Three selectors in the entire repository name a ``fieldname_`` class, all in
``kasvimuseo/static/css/kasvimuseo.admin.css``:

``#changelist-form td.fieldname_admin_thumbnail a img`` (line 19)
    **Dead.** This project's own ``admin/change_list.html`` renders
    ``<form id="grp-changelist-form">`` -- grappelli's id, confirmed in the
    rendered page -- so the selector has never matched anything.

``.fieldname_action_checkbox`` and ``.fieldname_edit`` (lines 39-40, in ``@media print``)
    The only live consumers. Of the two, ``.fieldname_action_checkbox`` is half
    live: the header cell of the checkbox column carries only Django's own
    ``action-checkbox-column`` (the fork's ``action_checkbox`` branch is
    verbatim Django), so printing a changelist hides the checkbox *body* cells
    and keeps the header -- the printed table's header row is one cell wider
    than its body. Django's own ``action-checkbox`` / ``action-checkbox-column``
    pair would do that job correctly with no fork at all.

So of the roughly 130 distinct ``fieldname_`` classes emitted across nine
changelists, exactly one -- ``fieldname_edit`` -- is genuinely consumed by CSS.
The rest are consumed only by ``test_admin_changelist.py``, which uses them to
address columns in twelve tests.

Django fixed the same ticket upstream in 1.7
--------------------------------------------

Django ticket #11195 is the fork's own cited source, and Django closed it in
**1.7**: "The admin changelist cells now have a ``field-<field_name>`` class in
the HTML to enable style customizations" (1.7 release notes). Stock
``items_for_result`` emits ``class="field-<name>"`` on cells and
``result_headers`` emits ``column-<name>`` on headers from 1.7 onwards. From
**1.10** stock also has ``_coerce_field_name``, which names a callable in
``list_display`` exactly as ``identifier_for_field`` does -- ``edit`` becomes
``field-edit`` -- differing only for lambdas, of which this project has none.
The 1.7 release also adds ``app-<app>`` and ``model-<model>`` classes to the
admin templates' ``<body>`` tag, which is the per-model CSS hook the project
does not have today.

The fork's whole reason to exist is therefore upstream from Stage 5, and
upstream including the callable case from Stage 8.

What carrying it costs, in the plan's terms
-------------------------------------------

Diffing the three forked functions between consecutive stage targets, 1.5.12
through 6.0.7: **15 of the 19 transitions change them, 343 changed lines in
total.** The largest are 3.2 -> 4.0 (96 lines), 1.6 -> 1.7 (80), 2.0 -> 2.1
(25), 4.2 -> 5.0 (23) and 1.8 -> 1.9 (22); four transitions change nothing.

Re-syncing is optional, though -- what is not optional is the imports. They
break at six points, and the plan's Part 3 table lists three of them:

============================== ======= ============================================
Symbol                         Gone in Where in the file
============================== ======= ============================================
``_meta.module_name``          1.8     ``identifier_for_field`` -- *not in Part 3*
``django.contrib.admin.util``  1.9     the import block
``EMPTY_CHANGELIST_VALUE``     1.9     ``items_for_result``, twice
``_meta.get_field_by_name``    1.10    ``identifier_for_field`` -- *not in Part 3*
``force_unicode``              2.0     ``identifier_for_field``
``force_text`` / ``smart_str`` 4.0     both, throughout
============================== ======= ============================================

``django.db.models.FieldDoesNotExist`` is a seventh: deprecated at 1.8 in favour
of ``django.core.exceptions.FieldDoesNotExist``, and also inside
``identifier_for_field``. Three of the seven are in the 31 lines the fork adds
to Django's code, and two of those three are in the branch issue 014 calls dead.

Decision
========

**Option 1 -- retire it -- with the deletion scheduled for Stage 5** rather than
done on Django 1.5.

Why not now. Django 1.5 emits no per-column class of its own, so retiring the
fork today means reproducing ``fieldname_edit`` some other way for four stages.
Neither route in the issue's option 1 is free: a ``format_html`` callable can
only fill a cell, not set the cell's ``class``, so ``@media print`` would leave
an empty column instead of no column; and ``nth-child`` needs scoping, because
``edit`` is column 2 in all nine of this project's ModelAdmins but photologue's
``PhotoAdmin`` has no Edit column and its column 2 is ``image_filename`` --
and the body class this project's ``change_list.html`` renders names no model.
On top of that, the twelve tests that address columns by class would have to
become positional. That is real work, and its whole benefit is four stages of
relief before Django hands the feature over anyway.

Why not option 2. It collapses into option 1. Its endpoint is "re-fork from
Django 6.0's source", but Django 6.0's source already emits these classes, so
the re-fork would be Django's own file with one string changed -- which is to
say, no fork. It would also still pay all six import repairs on the way, since
the file has to keep importing to keep running.

Why not option 3. 343 changed lines across 15 transitions, to keep a file whose
only distinguishing feature is available from stock at transition four.

What Stage 5 does, concretely
-----------------------------

#. Delete ``kasvimuseo/templatetags/kasvimuseo_admin_list.py`` and the
   ``{% load kasvimuseo_admin_list %}`` in
   ``kasvimuseo/templates/admin/change_list.html``, and restore that template's
   ``{% result_list cl %}`` -- Django's own tag, already loaded on the line
   above.
#. Make ``edit`` a ``ModelAdmin`` method named by a string in ``list_display``
   instead of the module-level callable it is today. Django 1.7's
   ``'field-%s' % field_name`` interpolates the callable itself, so a callable
   entry would render ``field-<function edit at 0x...>``; a string renders
   ``field-edit``. From 1.10 ``_coerce_field_name`` makes this unnecessary, but
   doing it at Stage 5 keeps the printed changelist correct for three stages.
#. In ``kasvimuseo/static/css/kasvimuseo.admin.css``: ``.fieldname_edit``
   becomes ``.field-edit, .column-edit``; ``.fieldname_action_checkbox`` becomes
   ``.action-checkbox, .action-checkbox-column``, which also fixes the header
   left behind in print today; and the dead
   ``#changelist-form td.fieldname_admin_thumbnail`` rule goes, since its
   ``#changelist-form`` has never matched grappelli's ``#grp-changelist-form``.
#. In ``kasvimuseo/tests/test_admin_changelist.py``: ``fieldname_X`` becomes
   ``field-X`` in the body and ``column-X`` in the header,
   ``test_identifier_for_field_branches`` goes with the function it tests, and
   ``test_action_checkbox_column`` asserts Django's two class names. The file's
   docstring stops describing a fork that no longer exists.

Until then the file is **frozen**: no stage before 5 edits it, and no stage
after 5 needs to, because it is gone. If a change to the changelist markup
becomes necessary before Stage 5, it belongs in the CSS or in ``admin.py``, not
in this file.

See also
========

The two issues this one blocks inherit different things.

**014** -- dead code inside the same file -- inherits a deletion date. Its
``Decision`` now records that the dead branch is not to be repaired: the file
goes at Stage 5, and two of the three API removals the plan had not listed are
in exactly that function. Its ``Status`` stays ``Open``, because the file is
still here; it closes when the file does.

**036** -- the upgrade programme -- inherits four fewer stage items and one more
Stage 5 step. Stages 6, 7, 10 and 17 no longer touch this file, Part 3's rows
for ``django.contrib.admin.util``, ``EMPTY_CHANGELIST_VALUE`` and
``force_unicode`` no longer point at any code, and the "recurring re-sync across
all nineteen stages" that ranked fourth in the plan's effort estimate is not
work anybody has to do. Its ``Status`` is unchanged.

``docs/upgrade-plan.rst`` Part 6, "The admin-list fork is deleted in
Stage 5",
carries the ruling, and Stage 5 carries the four steps above.
