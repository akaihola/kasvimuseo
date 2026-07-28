====================================================================
Issue 047: The label print toggle uses a glyph no Linux font has
====================================================================

:Status: Open
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
:Decision: undecided
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
* The control is invisible until hovered (``.remove { opacity: 0 }``), so on a
  touch screen it cannot be found at all. See issue 045.

Options
=======

1. Use ``&#x1f5a8;&#xfe0f;`` (``PRINTER`` with the emoji variation selector).
   Covered by Noto Color Emoji on Linux, by Apple Color Emoji on macOS and iOS,
   and by Segoe UI Emoji on Windows. It renders in colour, which is a visual
   change but a legible one.
2. Ship the icon rather than depend on the system: an inline SVG printer, which
   is the only option that looks the same everywhere and the only one that can
   be styled to match the rest of the page.
3. Drop the symbol and use the Finnish word, which the user guide already uses.

Whichever is chosen, fix the ``for`` attribute in the same change.

See also
========

Issue 045 (the same control on a touch screen), issue 046 (the same page's
zoom), issue 017 (nothing tests this page in a browser), issue 037 (the in-UI
instructions this control is missing from).
