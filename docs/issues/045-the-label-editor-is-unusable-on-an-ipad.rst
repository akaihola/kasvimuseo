=========================================================
Issue 045: The label editor is unusable on an iPad
=========================================================

:Status: Accepted
:Severity: Medium
:Area: templates / mobile
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: (none -- no test runs any page in a mobile browser; see issue 017)
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- nothing runs any page in a browser, let alone a tablet one
    046 -- the zoom, which is what makes the labels fit across the screen
    047 -- the print toggle, the control that needs the tap it never expected
    006 -- ``mobile-base.html``, the abandoned start of a mobile front end
    044 -- the other report that needed a browser to settle
:Decision: Scope confirmed by the maintainer on 2026-07-29: the admin, the
    label editor and the printable sheets. The admin already works there, so
    the work is the label editor and printing.
:Resolution: (none yet)

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

See also
========

Issue 046 (the zoom), issue 047 (the print toggle's glyph), issue 017 (the
browser suite that would have to catch a regression in any of this), issue 006
(which now also covers ``mobile-base.html``, the abandoned start of a mobile
front end), issue 044 (the other report that needed a browser to settle).
