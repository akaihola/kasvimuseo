================================================================
Issue 046: The label editor opens at print size, not screen size
================================================================

:Status: Accepted
:Severity: Low
:Area: templates / labels UI
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: (none -- no test looks at the page's rendered size; see issue 017)
:Depends on: (none)
:Blocks: (none)
:Related: 047 -- the same page, cheapest changed together
    045 -- the same page on a tablet, where this zoom is what makes it fit
    017 -- no browser test would notice either way
:Decision: Ruled by the maintainer on 2026-07-29: scale the labels to 50 % on
    screen; the printed sheet is unaffected. Option 1 below, with the value
    fixed rather than made adjustable.
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

On an iPad this stops being cosmetic
------------------------------------

The tablet report (issue 045) measured the same arithmetic at its worst: Safari
lays the page out at its 980px fallback width, 1138px are needed for two labels,
so the iPad shows **one label per row** -- and it cannot be zoomed out, because
Safari's minimum scale is already the one that fits 980px to the screen. The
browser-zoom workaround that exists on a desktop does not exist there. A screen
zoom of 50 % puts three labels across even that fallback viewport, which is what
makes the page usable on the device the gardeners carry.

Impact
======

On a desktop, cosmetic: a manual zoom every time the page is opened, which is a
browser preference the staff have to know about. On the iPad it is the
difference between arranging a print run and scrolling through it one label at
a time.

The fix
=======

Ruled on 2026-07-29: **50 % on screen, print unaffected** -- option 1 below,
with the value fixed rather than made adjustable.

1. **Scale the grid on screen only.** ``@media screen { #labels { zoom: 0.5 } }``
   leaves ``@media print`` untouched, so the printed sheet keeps its physical
   size. ``zoom`` reflows -- five labels per row on a 1440px window instead of
   two, three on the iPad's 980px fallback -- where ``transform: scale()`` would
   only shrink the same one- or two-per-row layout and leave the space beside
   them empty. It is non-standard but implemented in every current browser,
   including the Safari on the reported iPad.
2. **Make it a control**, not chosen: buttons or a slider next to ``Set box
   size``, defaulting to 50 % and remembered in ``localStorage`` or the query
   string. Recorded because it is the answer if different jobs later turn out to
   want different zooms.

Two things to do in the same change: tie the drag preview's ``0.25`` to the same
number, and say in the user guide that the on-screen size is not the printed
size. A test that a print run still measures 14cm would need the browser suite
of issue 017, which cannot run -- so until then, check it by printing to PDF
once.

See also
========

Issue 045 (the label editor on an iPad) and issue 047 (the print toggle's glyph)
-- the same page, and cheapest to fix together. Issue 017 is why none of this is
covered by a test.
