==========================================================
Issue 090: A split label flips when its photo loads
==========================================================

:Status: Fixed
:Severity: Low
:Area: browser tests / labels UI
:Reported: 2026-10-14
:Source: Task 17 in ``TASKS.md``. The ``playwright (chromium)`` job failed on
    the ``main`` runs of ``3f24d52``, ``b02822b``, ``99091e1``, ``ae9d28e``
    and ``d021683``, and passed on ``02d8c7c`` and ``d7bfff1``.
:Evidence: ``browser_tests/test_label_editor.py`` --
    ``test_dragging_a_number_onto_a_label_of_the_same_species_merges_them`` and
    ``test_a_number_moves_between_labels_by_touch`` are the tests that failed.
    Both now call ``labels_drawn`` before the second drag.
:Depends on: (none)
:Blocks: (none)
:Related: 045 -- the pointer drag these tests drive, and the ``touch-action``
    rule that turns a press beside the number into a cancelled gesture
    061 -- WebKit runs the mouse test and skips the touch one, so it never saw
    this
:Decision: Fix the tests, not the editor. The agent of task 17 decided this on
    2026-10-14 on the evidence below, as ``docs/issues/README.rst`` allows. The
    editor draws a label as soon as it exists and chooses the layout when the
    photo has loaded. That is correct behaviour for a photo that arrives over a
    network. A test that presses on a label within twenty milliseconds of
    creating it has to wait for that layout first. The maintainer confirms or
    changes this when they accept task 17.
:Resolution: a581695

This record is for the contributor who keeps the browser suite green. It
explains why a drag onto a label of the same species sometimes did not merge
in Chromium on CI, and what the tests now wait for.

Problem
=======

Both tests split number 11 off the narcissus label and then drag it onto the
narcissus label that remains. On the failing runs the second drag changed
nothing: the sheet still had two narcissus labels with one number each. The
failure happened only on the CI runner, only in Chromium, and in four of the
six ``main`` runs between 2026-10-11 and 2026-10-14. Eighty runs of the two
tests on a development machine passed, and so did sixty rounds with the
renderer slowed six times over the Chrome DevTools Protocol.

Cause
=====

A label is drawn horizontal when it is created. The editor's ``setAspect``
runs when the label's photo has loaded, and it turns the label vertical when
the photo is a portrait. The seeded narcissus photo is a portrait: it is
``valkonarsissi lehdet`` in ``browser_tests/seed.py``, 300 by 400 pixels. A
vertical label floats its numbers at the top right. A horizontal label places
them at the lower right.

The split label is created by the first drag, with its photo still to load.
The test then measured the centre of number 11 and pressed there. On the CI
runner the photo loaded between those two steps. The number had moved up by
53 pixels, and the press landed on the classification text below the photo.
That text has no ``touch-action: none``, so Chromium took the touch for a
pan and sent ``pointercancel``. The mouse variant pressed on the same text
and started no drag. In both cases the editor correctly moved nothing.

A development machine never shows this. Chromium serves the second copy of
the photo from its memory cache without a request, so the flip happens in the
same frame as the split, before the test can measure anything. The CI runner
is slow enough for the photo load to fall between the measurement and the
press.

Evidence
========

A probe, ``test_probe_task17.py`` in the task's work directory, disabled the
cache over the Chrome DevTools Protocol and held the photo response until the
test had measured the number. It then released the photo, waited for the flip,
and pressed where the number had been. The result was the failure CI showed.

.. list-table::
   :header-rows: 1

   * - Moment
     - Label 2 class
     - Number 11 rectangle
     - What the press hit
   * - Measured, photo pending
     - ``horizontal``
     - x 907, y 210, 39 by 20
     - --
   * - Photo loaded
     - ``vertical``
     - x 928, y 157, 18 by 18
     - ``p.classification``, then ``pointercancel``

The same probe ran the fixed sequence with every photo delayed by 150
milliseconds. Five rounds of five merged.

Fix
===

``labels_drawn`` in ``browser_tests/conftest.py`` waits until every label has
loaded its photo and carries the class its aspect ratio decides. ``open_editor``
calls it, so every editor test starts from a settled sheet. The two merge tests
call it again after their split, before they measure the number for the second
drag.

The editor is unchanged. Its brief horizontal-then-vertical redraw of a new
label is visible to a person only as a flicker on a slow connection. A later
change could copy the orientation from the label the number came from, since
both show the same photo; nothing depends on that today.

Verification
============

The two tests ran twenty times in Chromium and twenty times in WebKit after
the fix, and the full browser suite ran once in each engine. The task
description in ``docs/tasks/`` records the counts. The remaining check is the
``playwright (chromium)`` job on three consecutive pushes to ``main``.
