=========================================================
Issue 045: The label editor is unusable on an iPad
=========================================================

:Status: Fixed
:Severity: Medium
:Area: templates / mobile
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: ``kasvimuseo/tests/test_templates.py`` --
    ``test_report_pages_lay_out_at_the_device_width``,
    ``test_the_public_base_template_lays_out_at_the_device_width``,
    ``test_printable_pages_offer_a_print_button`` and
    ``test_the_label_print_toggle_needs_no_hover`` assert the markup of the
    cheap half, and cannot see what any of it *does*. What the large half does
    is in ``browser_tests/test_label_editor.py``, which 017 made runnable:
    ``test_a_number_moves_between_labels_by_touch`` and the four tests around
    it drive a real touch screen, and the two mouse drag tests that were there
    before now go through the same pointer handlers
:Depends on: (none -- 044 briefly blocked *verifying* this on the device, since
    it truncated the label editor's data endpoint too and the page then drew
    nothing at all in a browser; it is fixed, and this is rebased onto it)
:Blocks: (none)
:Related: 017 -- the browser suite that had to exist before this rewrite could
    046 -- the zoom, which is what makes the labels fit across the screen
    047 -- the print toggle, the control that needs the tap it never expected
    006 -- ``mobile-base.html``, the abandoned start of a mobile front end
    044 -- the other report that needed a browser to settle
:Decision: Scope confirmed by the maintainer on 2026-07-29: the admin, the
    label editor and the printable sheets. The admin already works there, so
    the work is the label editor and printing. The cheap half of "The work, in
    two halves" is done; the large half -- pointer events instead of HTML5 drag
    and drop -- is not, and wants issue 017 first. The viewport tag went into
    five templates rather than three; the print button is a wrapped
    ``<button>`` with one rule in the sheets' own print stylesheet; and the
    toggle's ``opacity: 0`` was dropped rather than ``:focus-within`` added,
    because nothing focuses that checkbox until it is tapped and the complaint
    is that there is nothing visible to tap. The three are argued in "What the
    cheap half decided" below. The large half was taken once 017 was fixed, and
    it decided three things: pointer events replace the HTML5 drag layer
    outright rather than being added beside it, so a mouse and a finger take
    the same path and there is one interaction to keep working; the sheet is
    rearranged **on release** rather than while the pointer passes over labels,
    because a pointer drag belongs to the element it started on and the old
    live preview worked by deleting that element mid-gesture; and the label a
    number lands on is found by hit-testing the release point, since a pointer
    drag is not delivered to what it passes over. Argued in "What the large
    half decided" below.
:Resolution: The cheap half is fixed in bffb370, with the print toggle's
    pointer split in 64ddc1b and its colour on an excluded label in 17e9c4c.
    The large half -- pointer events, and the touch tests that hold them up --
    is fixed in COMMIT, which is what makes this ``Fixed``.

Problem
=======

"Ensure everything works on an iPad" came in as one sentence. It now has a
device and a list of symptoms:

==================== ==============================================
 Device              iPad (7th generation), iPadOS 18.7.9, Safari
 In scope            admin, label editor, printable sheets
 Admin               **Works.**
 Label editor        Numbers cannot be dragged between labels.
                     The hide/show checkbox appears only after
                     tapping a label. The page cannot be zoomed
                     out, and shows one label per row.
 Printing            No way found to print from Safari.
==================== ==============================================

The tablet is the natural device for this application: the users are gardeners,
the data is entered where the plants are, and every page is either the admin or
a report rendered from it. That the admin works is the good news in this
report -- Grappelli's desktop layout is serviceable on a 10-inch screen, so the
work is confined to the label editor and to printing.

Each symptom has a cause in the templates
=========================================

**Numbers cannot be dragged.** ``reports/planting-labels.html`` moves museum
numbers between labels with the HTML5 drag-and-drop API -- ``dragstart``,
``dragenter``, ``dragover``, ``drop``. iOS Safari does not generate those events
from touch, and never has. The editor's central interaction is not degraded on
an iPad, it is absent. Only the photo arrows and the save button respond.

**The hide/show checkbox appears only after tapping.** It is hidden until the
pointer is over the label::

    .remove { opacity: 0; }
    li:hover .remove { opacity: 0.5; }

A touch screen has no hover, so Safari fakes one on the first tap -- which is
why the control appears on a tap that was meant to do something else, and why
it is invisible until then. Issue 047 covers the same control's glyph and its
inert ``<label for>``.

**One label per row, and no way to zoom out.** No template in this repository
contains ``<meta name="viewport">``, so Safari lays the page out at its 980px
fallback width and scales that to fit the screen. A default label is 14cm wide
plus 0.5cm margins, about 569 CSS px, so two need 1138px and only one fits in
980. The same fallback is why the page will not zoom out: Safari's minimum
scale is the one that fits the layout viewport to the screen, and that is
already where the page starts.

Note which fix does what here, because they pull in opposite directions. Adding
``<meta name="viewport" content="width=device-width, initial-scale=1">`` makes
the layout viewport 810px in portrait and 1080px in landscape on this device --
text becomes legible at 1:1, which is the fix for the admin and the report
pages, but the labels get *larger*, and 1138px still does not fit in 1080. What
puts several labels across the screen is issue 046's screen zoom: at 50 % a
label is about 285px, so three fit across even the 980px fallback.

**No way to print.** iPadOS Safari's print command lives in the Share menu, not
on a toolbar, and none of the printable pages offers a control of its own. The
label editor already hides ``form``, ``.hidden`` and ``button`` in
``@media print``, so a ``<button onclick="window.print()">`` would cost one line
and never appear on the paper. The species sheets need the same.

Impact
======

The label editor is the one page in the application that exists to be operated
by hand, and on the tablet the gardeners carry it can neither be rearranged nor
printed. Everything else on the device is usable today.

The work, in two halves
=======================

**Cheap, and worth doing whatever is decided about the rest:**

1. A viewport meta tag in each base template -- ``ylaneenkasvit/templates/
   base.html`` and the report bases. One line each.
2. A print button on the label editor and on the species sheets, hidden in
   ``@media print``.
3. Make the print toggle visible without a hover -- drop the ``opacity: 0``, or
   reveal it on ``:focus-within`` as well. Take issue 047 first: it is already
   changing that markup, and that hover is the only thing keeping the control
   off the printed sheet, so 047 adds ``.remove`` to the ``@media print`` hide
   list before this step removes the accident it relies on.
4. Issue 046's screen zoom, which is what actually makes the sheet readable
   across the screen.

**Large, and needs a decision of its own:** replacing the drag-and-drop layer
with pointer events, so numbers can be moved by touch. That is a rewrite of the
one part of the Vue application with no test coverage at all, on a page whose
browser suite cannot run (issue 017). Doing it without first making 017's suite
runnable means rewriting the editor's core interaction blind, which is an
argument for taking 017 first even though it fixes nothing by itself.

What the cheap half decided
===========================

**The viewport tag went into five templates, not three.** Every template with a
``<head>`` that a tablet reaches: ``ylaneenkasvit/templates/base.html`` (which
had no ``<head>`` at all, and is what photologue's pages extend), the two
report bases, and the label editor, which extends nothing. The species list and
the compact base reach ``<head>`` only through django-jqm's vendored
``jqm/v1_1_0.html``, which lives in site-packages and cannot be edited from
here, so their tag goes in ``{% block sitestyle %}`` -- the one block that
template leaves inside ``<head>``. Not added to ``mobile-base.html``, which was
dead and has since been deleted by issue 006, nor to the observation page or
the bed map, both outside this issue's scope.
One trap on the way: a multi-line ``{# ... #}`` is not a comment in Django 1.5,
so the comments explaining the tag are ``{% comment %}`` blocks -- the first
attempt rendered its own explanation onto every page.

**The print button is a wrapped ``<button>``.** On the label editor
``@media print`` already hides every ``button``, so one line was enough. The
sheets have print CSS of their own -- ``static/css/planted-species-printable
.css``, which hid ``nav`` and nothing else -- and both bases link it, so a
single ``.print-sheet { display: none }`` there covers both. The class sits on
a wrapper ``<div>`` rather than on the button, because jQuery Mobile replaces
the button with a container of its own and ``display: none`` on the inner
element would leave that container on the paper.

**``opacity: 0`` dropped, not ``:focus-within`` added, and then split by
pointer type.** ``:focus-within`` was never the answer: nothing focuses that
checkbox until it is tapped, and the complaint is that there is nothing visible
to tap. Dropping the ``opacity: 0`` outright fixed the tablet but took away
something the mouse users had -- a sheet with no controls drawn over it -- so
the maintainer asked for both, and the rule is now split on whether the device
can hover at all:

* **No hover** (the iPad, and any touch-only screen): the dimmed printer and
  its checkbox are simply always drawn. There is no gesture that could reveal
  them, so there is nothing to reveal them *with*.
* **A mouse** (``@media (hover: hover)``): hidden at rest, dimmed to 0.5 while
  the pointer is moving or the page is scrolling, and full over the label the
  pointer is on. A two-second timer takes them away again. The activity class
  is set by six lines of script at the top of the page's own ``<script>``,
  guarded by the same ``matchMedia('(hover: hover)')``, so a touch device never
  runs it.

The toggle looks the same on every label, whatever its state. That took one
more change than it sounds: a label left out of the print run was dimmed with
``opacity: 0.3`` on the ``li``, which makes a **compositing group**, so
everything inside it -- the toggle included -- is composited against that 0.3
however opaque its own rule says it is. The toggle came out 89 levels of grey
paler on an unchecked label than on a checked one, in both of its states, while
``getComputedStyle`` reported the same ``0.5`` for both; no computed-style
assertion could have caught it, and the pixels had to be sampled. The dimming
now applies to the label's *contents* (``li.hidden > *:not(.remove)``) with the
border toned down separately, so the toggle is outside the group and renders
identically either way -- measured at 126/255 against 126/255, was 126 against
215.

All of it is safe only because issue 047 put ``.remove`` in the ``@media print``
hide list; that line was verified present before the opacity went, and the
printed sheet was checked again afterwards.

What landed, and what it measures
=================================

Steps 1 to 3 of the cheap half; step 4 was issue 046 and is already on
``master``. Measured in headless WebKit and Chromium at the device's metrics --
**this is emulation, not the device**, and the reporter has the iPad and can
confirm. The pages were rendered by Django, dumped, and served locally, with
the CDN copies of Vue, axios and sanitize.css replaced by local ones; jQuery
Mobile has no copy this sandbox can fetch, so the two jqm pages were measured
unstyled. Both engines agreed on every number below.

==================================== ================== ==================
 Measurement                          Before             After
==================================== ================== ==================
 Layout viewport, portrait            980px              810px
 Layout viewport, landscape           1080px             1080px
 First content element at 1440px      same box           same box
 Print button on screen               absent             visible
 Print button in ``@media print``     --                 ``display: none``
 Print toggle, touch, at rest         ``opacity: 0``     ``opacity: 0.5``
 Print toggle, mouse, at rest         ``opacity: 0``     ``opacity: 0``
 Print toggle, mouse, moving          ``opacity: 0``     ``opacity: 0.5``
 Print toggle, mouse, label hovered   ``opacity: 0.5``   ``opacity: 1``
 Print toggle in ``@media print``     ``display: none``  ``display: none``
 Toggle ink, checked label            126/255            126/255
 Toggle ink, unchecked label          215/255            126/255
 Labels across, portrait              3                  2
 Labels across, landscape             3                  3
==================================== ================== ==================

The landscape row is why the tag is not the whole answer: the 980px fallback is
a *minimum*, so a 1080px-wide window already laid out at 1080 and the tag
changes nothing there. In portrait the tag makes the layout viewport *narrower*,
which is the legibility fix for the admin and the sheets and costs the label
editor one label per row at 046's 50 % zoom -- exactly the trade-off "Each
symptom has a cause in the templates" predicts. It is a trade worth making
here: two legible labels beat three unreadable ones, the sheet is arranged
rather than read, and landscape still shows three.

The four toggle rows were taken in a touch context (``hover: none``,
``pointer: coarse``) and a mouse one, in both engines: touch holds 0.5 with no
input at all and after three seconds of stillness; a mouse shows nothing until
the pointer moves or the page scrolls, 0.5 then, 1 on the label under the
pointer while its neighbours stay at 0.5, and 0 again three seconds after the
pointer stops.

The two ink rows are the darkest pixel of the printer glyph itself, sampled
from a screenshot of the control rather than read out of ``getComputedStyle``,
which reports 0.5 in every one of those four cells and so cannot tell the
states apart.

Printing each page to PDF puts neither print button on the paper, and the print
toggle is not on it either -- checked again after the toggle was split by
pointer type, since a mouse-only rule must not be what keeps it off the paper.

**Still not confirmed on the device.** Everything above is emulation. It could
not have been confirmed until 2026-07-31 for a reason outside this issue: the
label editor's data endpoint was among the responses issue 044's pasta layer
truncated -- cut off mid-string around 42.9 kB, so ``JSON.parse`` raised and the
Vue application drew nothing at all in a browser talking to the development
server. 044 is fixed (``76f5b9c``), and this branch is rebased onto that fix, so
the page loads and the maintainer can now look at it on the iPad. The numbers
above come from a dump taken through the Django test client, which never crossed
a socket and was therefore always complete.

What the large half decided
===========================

Issue 017 is fixed, so the interaction with no coverage now has some, and the
rewrite was taken. The drag-and-drop layer is gone: ``draggable``,
``dragstart``, ``dragend`` and the ``dragenter`` / ``dragover`` / ``drop``
handlers on the ``<ul>`` and on every label are replaced by ``pointerdown`` on
a museum number and ``pointermove`` / ``pointerup`` / ``pointercancel`` on
``window`` while one is being moved.

**Replaced, not added beside.** A mouse produces pointer events too, so there
is one interaction rather than a touch one and a mouse one that can drift
apart. The two mouse drag tests that were already in
``browser_tests/test_label_editor.py`` did not change and now exercise the new
code, which is the assurance that nothing was lost; the reverse -- keeping drag
and drop for the mouse and adding pointer events for touch -- would have meant
two code paths and a browser deciding which one to fire.

**The sheet is rearranged on release, not on the way.** This is the change with
consequences. The old code moved the number into whichever label the drag
entered, took it out again on leaving, and put it back on ``dragend`` if the
drop was refused, so the dragged ``<p>`` was deleted and recreated repeatedly
during a gesture. A pointer drag cannot survive that: the events belong to the
element the gesture started on -- on touch the browser captures to it
implicitly -- so deleting that element mid-gesture is exactly what must not
happen. Committing on release also makes a cancelled gesture free: there is
nothing to undo, which is what
``test_a_touch_gesture_the_system_takes_away_changes_nothing`` pins.

**The target is hit-tested, not entered.** Nothing receives a pointer drag as
it passes over, so ``dropTarget`` asks ``document.elementFromPoint`` what is
under the release point and takes the ``li`` it is in, the ``<ul>`` background,
or nothing at all. That made ``#drag-wrapper``, the preview, the one thing that
would always be under the pointer, so it is now ``pointer-events: none``; its
``z-index: -1``, which the old code used for the same purpose, is not enough
when the point is over the empty part of the sheet.

**A tap is not a drag.** A finger is never still, so a press moves nothing
until it has travelled five pixels. Without it every tap on a number would
rearrange the sheet -- worse than the defect being fixed -- and the print
toggle, which is the other thing on a label to tap, sits next to it.

**The gesture is taken from the browser explicitly.** ``touch-action: none`` on
``.observation-id`` stops a touch that starts on a number becoming a scroll or
a double-tap zoom, and ``user-select: none`` there stops a mouse drag selecting
the digits instead of moving them; ``preventDefault()`` on ``pointerdown`` does
the rest. All three belong on the number, not on the document.

**Nothing new listens on the page at rest.** ``pointerdown`` is bound on the
numbers by Vue, and the three window listeners are added when a drag starts and
removed when it ends. The six lines that dim the print toggles in on a mouse
listen for ``mousemove`` and ``scroll``, passively, and were not touched: the
toggle behaviour this issue's cheap half and issue 047 settled is exactly as it
was, and ``.remove`` is still in the ``@media print`` hide list.

**The preview follows the pointer for the whole drag** rather than only over
the background, because on a touch screen the finger covers the number and the
preview is the only feedback there is. It still reads ``--screen-scale`` and
still offsets by 380 x 120 unscaled pixels, so it matches the grid at issue
046's 50 %;
``test_the_drag_preview_follows_the_finger_at_the_screen_zoom`` reads the
computed matrix and would fail if either constant moved without the other.

**Enabling Save is now deliberate.** It used to be a side effect: showing the
preview set ``dragSpecies.visible``, and the label component's watcher reported
that as an edit. So what enabled the button after a drag was passing over the
gap between two labels, not moving anything. A completed move now emits
``enable-save`` itself, and the preview is marked ``:preview`` so its watchers
say nothing -- otherwise a gesture that landed nowhere would offer to save a
sheet nobody had changed.

What it was tested with, and what it was not
============================================

``browser_tests/test_label_editor.py`` grew six tests and a second browser
context. The touch ones drive an emulated iPad: ``has_touch``, ``is_mobile``
and 1080 x 810, which is the device landscape, and at 50 % zoom is three labels
across with empty sheet beside them. The gesture is dispatched over the Chrome
DevTools Protocol -- ``Input.dispatchTouchEvent`` -- rather than by calling a
handler or constructing a ``PointerEvent`` in the page, so the browser does its
own hit-testing, applies ``touch-action`` and decides for itself what pointer
events to generate.

=========================================== ================================
 What it asserts                             How
=========================================== ================================
 A number moves to another label by touch    Two touch drags: one splits the
                                             label, one merges it back
 The same by mouse                           The two drag tests that were
                                             there before, unchanged
 A tap moves nothing                         ``touchscreen.tap`` on a number
 A cancelled gesture changes nothing         ``touchCancel`` mid-drag
 A release off the sheet changes nothing     Mouse, released on the Save
                                             button
 The preview tracks at 50 %                  The computed transform matrix,
                                             mid-drag
 The save cycle keeps the arrangement        Touch drag, save, reload
=========================================== ================================

Four of the six fail against the previous template, which is the point of
writing them: the two that pass are the ones asserting that nothing happens,
and before the rewrite nothing was what touch did anyway.

**What this is not.** It is Chromium with touch emulation, not an iPad, and the
engine that matters is iOS Safari's. The suite runs Chromium only:
``Input.dispatchTouchEvent`` is a Chrome DevTools Protocol call and WebKit has
no such thing, while Playwright's synchronous ``touchscreen`` can only tap, so
the touch drag cannot be expressed against WebKit at all without giving up the
browser's own event generation -- which is the half worth testing. Left for the
maintainer, who has the device:

* that iOS Safari raises ``pointerdown`` / ``pointermove`` / ``pointerup`` from
  a finger on this page at all, and that ``touch-action: none`` is what keeps
  Safari from taking the gesture as a scroll or a page zoom;
* whether Safari's own gestures interrupt a drag -- the selection loupe, the
  tap-and-hold callout, an edge swipe -- and whether the ``pointercancel``
  handling is enough when one does;
* that a 285-pixel preview under a finger is usable feedback on a 10-inch
  screen, which is a judgement no assertion makes;
* the cheap half's own measurements, which were headless WebKit and Chromium
  at the device's metrics and have not been confirmed on the device either.

What is left
============

Nothing in this issue. The reported symptom -- numbers cannot be dragged
between labels -- is fixed, and the four bullets above are confirmations to
make on the device rather than work this repository can do. Printing from
Safari's Share menu remains as the cheap half left it: the button is there and
does not print itself.

See also
========

Issue 046 (the zoom), issue 047 (the print toggle's glyph), issue 017 (the
browser suite that would have to catch a regression in any of this), issue 006
(which also covered ``mobile-base.html``, the abandoned start of a mobile front
end, and deleted it), issue 044 (the other report that needed a browser to settle).
