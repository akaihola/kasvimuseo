================================================================
Issue 046: The label editor opens at print size, not screen size
================================================================

:Status: Open
:Severity: Low
:Area: templates / labels UI
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: (none -- no test looks at the page's rendered size; see issue 017)
:Depends on: (none)
:Blocks: (none)
:Related: 047 -- the same page, cheapest changed together
    045 -- the same page on a tablet, where the zoom is a pinch
    017 -- no browser test would notice either way
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``reports/planting-labels.html`` sizes each label in physical units, because
the same markup is what the printer gets::

    li {
        width: {{ request.GET.width|default:"14cm" }};
        height: {{ request.GET.height|default:"8cm" }};
        margin: 0.5cm;
    }

At the CSS reference of 96px per inch a default label is about 529 x 302 px
plus margins, so a 1440px window shows two labels per row and a handful of rows.
Reviewing a print run of dozens of labels means scrolling past all of them at a
size nobody needs on screen. The reporter's remedy today is the browser's own
zoom control, and puts the right value at **50 %**.

The page has no zoom of its own. Its only size control is the ``Box width`` /
``Box height`` form, and that is not the same thing: it is a GET parameter that
changes the printed label, not how large it looks while being arranged.

One detail to keep in step: the drag preview is already scaled, and by a
different amount. ``#drag-wrapper`` carries ``transform: scale(0.25)`` in the
stylesheet, and ``dragOverBackground`` rewrites the same transform inline while
the pointer moves::

    this.mouse = `transform: translate(${x}px, ${y}px) scale(0.25);`;

Both are hardcoded, in two places, and the ``-95`` / ``-30`` pointer offsets in
that method are tuned to the resulting size. Whatever sets the page's screen
scale has to set these too, or the label being dragged stops matching the
labels it is dropped onto.

Impact
======

Cosmetic, and it costs a manual zoom every time the page is opened -- on a
device where that is a browser preference the staff have to know about, and on
an iPad (issue 045) a pinch that also has to be undone before printing.

Options
=======

1. **Scale the grid on screen only.** ``@media screen { #labels { zoom: 0.5 } }``
   leaves ``@media print`` untouched, so the printed sheet keeps its physical
   size. ``zoom`` reflows -- five labels per row instead of two -- where
   ``transform: scale()`` would only shrink the same two-per-row layout and
   leave the space beside them empty. It is non-standard but implemented in
   every current browser.
2. **Make it a control.** Buttons or a slider next to ``Set box size``,
   defaulting to 50 % and remembered in ``localStorage`` or the query string.
   More work, but it is the honest answer if different jobs want different
   zooms, and it puts the setting where the person arranging labels can see it.

Either way, tie the drag preview's ``0.25`` to the same number, and say in the
user guide that the on-screen size is not the printed size.

See also
========

Issue 045 (the application on an iPad) and issue 047 (the print toggle's glyph)
-- the same page, and cheapest to fix together. Issue 017 is why none of this is
covered by a test.
