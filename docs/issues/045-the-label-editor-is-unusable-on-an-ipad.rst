=========================================================
Issue 045: The label editor is unusable on an iPad
=========================================================

:Status: Accepted
:Severity: Medium
:Area: templates / mobile
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: ``kasvimuseo/tests/test_templates.py`` --
    ``test_report_pages_lay_out_at_the_device_width``,
    ``test_the_public_base_template_lays_out_at_the_device_width``,
    ``test_printable_pages_offer_a_print_button`` and
    ``test_the_label_print_toggle_needs_no_hover`` assert the markup of the
    cheap half. They cannot see what any of it *does*: no test runs a page in a
    browser, mobile or otherwise (issue 017)
:Depends on: (none -- 044 briefly blocked *verifying* this on the device, since
    it truncated the label editor's data endpoint too and the page then drew
    nothing at all in a browser; it is fixed, and this is rebased onto it)
:Blocks: (none)
:Related: 017 -- nothing runs any page in a browser, let alone a tablet one
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
    cheap half decided" below.
:Resolution: The cheap half is fixed in bffb370, with the print toggle's
    pointer split in 64ddc1b; the large half is open, so ``Status`` stays
    ``Accepted``. See "What is left" below.

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
template leaves inside ``<head>``. Not added to ``mobile-base.html`` (dead,
issue 006), the observation page or the bed map, all outside this issue's scope.
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

A hidden label's toggle stays at full strength inside the 0.3 dimming, since it
is the one control that puts the label back -- on a mouse that too waits for
the pointer to move. All of it is safe only because issue 047 put ``.remove``
in the ``@media print`` hide list; that line was verified present before the
opacity went, and the printed sheet was checked again afterwards.

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

What is left
============

The large half, untouched: numbers still cannot be dragged between labels by
touch, because ``dragstart`` / ``dragenter`` / ``dragover`` / ``drop`` are not
generated from touch and never have been. That is the reported symptom this
change does *not* fix. It wants **issue 017 first**: the rewrite is of the one
part of the Vue application with no test coverage, and until 017's browser
suite runs there is nothing that would catch a regression in it. ``Status``
stays ``Accepted`` for that reason.

See also
========

Issue 046 (the zoom), issue 047 (the print toggle's glyph), issue 017 (the
browser suite that would have to catch a regression in any of this), issue 006
(which now also covers ``mobile-base.html``, the abandoned start of a mobile
front end), issue 044 (the other report that needed a browser to settle).
