====================================================================
Issue 047: The label print toggle uses a glyph no Linux font has
====================================================================

:Status: Accepted
:Severity: Medium
:Area: templates / labels UI
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: (none -- the suite asserts the page's server contract, not its glyphs)
:Depends on: (none)
:Blocks: (none)
:Related: 046 -- the same page, cheapest changed together
    045 -- the same control, hover-only, on a screen with no hover
    037 -- the instructions this control is missing from
    017 -- no browser test would notice either way
:Decision: Ruled by the maintainer on 2026-07-29: an inline SVG printer, and
    clicking it must toggle the checkbox. Option 2 below, with the ``<label>``
    defect fixed in the same change rather than left as a follow-up.
:Resolution: (none yet)

Problem
=======

Each label in ``reports/planting-labels.html`` carries a printer symbol beside
the checkbox that decides whether the label is printed::

    '<div class="remove">' +
    '     <label for="remove">&#x1f5b6;</label>' +
    '<input type="checkbox" v-model="species.visible">' +
    '</div>'

``U+1F5B6`` is ``PRINTER ICON``, one of the Wingdings characters added to
Unicode 7.0. It was never given an emoji presentation, so the emoji fonts do
not carry it, and on Linux essentially nothing else does either. On the
development machine::

    $ fc-list ':charset=1f5b6' family     # (nothing)
    $ fc-list ':charset=1f5a8' family
    Noto Color Emoji

``U+1F5A8`` ``PRINTER`` -- the emoji-presentation printer -- is covered;
``U+1F5B6`` is not. Where the control should show a printer, Linux shows the
replacement box.

Impact
======

The one control that decides what comes out of the printer is unlabelled on
Linux. The user guide describes it by appearance -- "poista tulostusrasti
kyltin oikeassa alalaidassa" -- so the instructions do not match the screen.
The checkbox beside it still works, so nothing is lost but the meaning.

Two further defects in the same three lines
===========================================

* ``<label for="remove">`` points at an id that does not exist. Nothing in the
  template has ``id="remove"``, so the label is inert: clicking the printer
  symbol does not toggle the checkbox, which is the whole reason to have a
  ``<label>``. Vue renders one copy of this markup per label, so a single
  shared id would be wrong anyway -- it needs a per-label id, or the checkbox
  wrapped inside the ``<label>`` element, which needs no id at all.
* The control is invisible until hovered (``.remove { opacity: 0 }``). On the
  iPad of issue 045 this is confirmed rather than predicted: it appears only
  after a tap that was meant to do something else, because Safari fakes the
  hover on first touch.

The fix
=======

Ruled on 2026-07-29: **an inline SVG printer, and clicking it toggles the
checkbox** -- option 2 below, with the ``<label>`` defect fixed in the same
change.

Wrapping the checkbox in the ``<label>`` is what makes the click work, and it
is also the only form of the fix that survives ``v-for``: an ``id`` would have
to be made unique per label, while a wrapping label needs none::

    '<div class="remove">' +
    '    <label><svg viewBox="0 0 24 24" aria-hidden="true">…</svg>' +
    '           <input type="checkbox" v-model="species.visible"></label>' +
    '</div>'

The Vue templates are single-quoted JavaScript strings, so an SVG's double
quotes need no escaping. Draw the path with ``fill="currentColor"`` so it takes
the colour of its surroundings, and set its size in CSS -- ``.remove svg { }``
replacing the ``font-size: 30pt`` that sized the glyph.

Two things to get right in the same change
------------------------------------------

**It must still not print.** Today the control is kept off the paper by
accident: ``@media print`` hides ``form``, ``.hidden`` and ``button``, and the
toggle is none of those -- it is invisible on paper only because
``.remove { opacity: 0 }`` and there is no hover while printing. The moment
that opacity goes, which is what issue 045 asks for so the control can be found
on a touch screen, the printer icon starts appearing on every label. Add
``.remove`` to the ``@media print`` hide list in this change, before the
behaviour that depends on it changes.

**Check it by printing.** No test can see this: the browser suite cannot run
(issue 017), and the server-side tests assert the page's contract, not its
glyphs. Verify by eye on Linux, and by printing one sheet to PDF to confirm the
icon is absent from it.

Rejected alternatives, recorded so they are not revisited
---------------------------------------------------------

1. ``&#x1f5a8;&#xfe0f;`` (``PRINTER`` with the emoji variation selector) --
   covered by Noto Color Emoji on Linux, Apple Color Emoji on macOS and iOS,
   Segoe UI Emoji on Windows. Would work, but renders in whatever colour the
   system emoji font chooses, which cannot be styled to match the page.
2. The Finnish word, which the user guide already uses. Cheapest, but it is a
   wide piece of text in a corner that has room for a glyph.

See also
========

Issue 045 (the same control on a touch screen), issue 046 (the same page's
zoom), issue 017 (nothing tests this page in a browser), issue 037 (the in-UI
instructions this control is missing from).
