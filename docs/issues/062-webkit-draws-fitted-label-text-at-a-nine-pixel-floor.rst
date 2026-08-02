===============================================================
Issue 062: WebKit draws fitted label text at a nine-pixel floor
===============================================================

:Status: Open
:Severity: Medium
:Area: templates / labels UI
:Reported: 2026-08-02
:Source: Measured while running the browser suite in WebKit for the first time
    (issue 061)
:Evidence: ``browser_tests/test_label_editor.py`` --
    ``test_a_fitted_name_is_drawn_at_the_size_it_was_fitted_to`` pins what each
    engine does today: in Chromium the drawn size equals the inline size fitty
    wrote, in WebKit it is strictly larger. The sweep behind it is in
    "Measured" below
:Depends on: (none -- it is measurable and reproducible here, and what it is
    waiting for is a ruling between three answers)
:Blocks: (none)
:Related: 046 -- the ``zoom: 0.5`` this is entirely a consequence of
    056 -- the same page, the same symptom family, and the report that says
    Safari's measurements are the load-bearing question
    045 -- the tablet the symptom was reported from
    061 -- the engine parametrisation that found this
:Decision: undecided -- three options below, and the ruling wants an answer to
    "how small may a species name be drawn on the sheet?", which is a question
    about the printed and on-screen product rather than about the template
:Resolution: (none yet)

Problem
=======

``reports/planting-labels.html`` fits each species name to its label with
fitty, which writes the result as an inline ``font-size``. The sheet is drawn
at ``zoom: 0.5`` on screen (issue 046).

In WebKit -- the engine iOS Safari is built on, and the one every report about
this page has come from -- text inside that zoomed subtree is never drawn
smaller than 9 used pixels. At ``zoom: 0.5`` that is a floor of 18 specified
pixels, so **a name fitty fits to anything between 9px and 18px is drawn at
18px**: up to twice the size it was fitted to, in the direction that makes it
not fit.

Chromium draws what fitty asked for, which is why nothing here was visible
before 061 ran this suite in a second engine.

Measured
========

The species name of the first label, with a name long enough to need fitting
and its photo failed, at the desktop metrics the suite uses:

======================================== ========== ==========
 Measurement                              Chromium   WebKit
======================================== ========== ==========
 Inline ``font-size`` fitty wrote         16px       16px
 ``getComputedStyle`` reports             16px       **18px**
 Drawn height of the ``h1``               17.59px    19.80px
======================================== ========== ==========

Sweeping the inline size on that same element says what the rule is. Inside
``#labels`` at ``zoom: 0.5``:

========== ========== ==========
 Specified  Chromium   WebKit
========== ========== ==========
 4px        4px        4px
 8px        8px        8px
 9px        9px        **18px**
 12px       12px       **18px**
 16px       16px       **18px**
 17px       17px       **18px**
 18px       18px       18px
 20px       20px       20px
 30px       30px       30px
========== ========== ==========

Two controls, on the same element in the same page, say it is the zoom and not
the text:

* with ``zoom`` set back to ``1``, WebKit reports every one of those sizes
  unchanged -- 9px is 9px;
* with the same 50 % scale expressed as ``transform: scale(0.5)`` instead of
  ``zoom``, WebKit again reports every size unchanged.

So the mechanism is WebKit's minimum font size applied to the *used* size after
the zoom multiplies it, and reported back in the unzoomed coordinate system.
Sizes already below the floor before zooming (4px, 8px) are exempt, which is
the shape WebKit's minimum-size logic has always had.

``-webkit-text-size-adjust: none`` on the element does not change it, which
rules out the text-autosizing suspect 056 named -- for this symptom. That was
worth checking and is not what this is.

What this is not
================

* **It is not 056.** 056's first half is text that was never fitted at all;
  this is text that was fitted and then drawn bigger. 056's second half is
  growth over seconds on the device; this is a fixed floor that does not move.
  Nothing here changes what 056 says, and its ``Status`` is untouched.
* **It is not established on the iPad.** Playwright's WebKit on Linux is
  Safari's engine, not Safari, and a minimum font size is a setting an
  embedder chooses. Whether iOS Safari applies the same floor is one look at
  the device -- see "What is left". What *is* established is that the size
  fitty computes is not necessarily the size drawn, on an engine of that
  family, which is a fact about the template rather than about a browser
  build.
* **It is not the drag preview.** ``#drag-number`` is outside ``#labels`` and
  takes no zoom, so it is not this.

Why it matters
==============

The whole point of fitting is that a long name fits its label. Where WebKit
applies the floor the name is drawn 12 % to 100 % larger than the size that was
computed to make it fit, so it can overflow the label it was fitted into --
which is what a gardener sees, and it is the family of symptom 045 and 056 were
both reported as. On this data the effect is 16px drawn at 18px; on a longer
name -- and the register's own test data uses one -- the gap is larger, and it
closes only when the fit lands at 18px or above, or below 9px where the floor
stops applying.

Three options
=============

1. **Do nothing until the device says so.** Cheapest, and defensible: the
   measurement is from a Linux WebKit build, and if iOS Safari has no such
   floor there is nothing here to repair. The cost is that the sheet's fitting
   remains something the suite cannot hold to its own arithmetic on the engine
   that matters, and the next report of "the text does not fit" starts here
   again.
2. **Never fit below the floor.** Give ``fitTextToSpace`` a minimum of 18px
   specified and let a name that still does not fit be handled deliberately --
   wrapped, or allowed to overflow. Both engines then draw the same thing, and
   what a very long name does becomes a decision somebody made rather than a
   browser setting. It needs the ruling in ``Decision``, because it is a
   statement about the smallest a name may be printed.
3. **Scale the sheet with a transform instead of ``zoom``.** Measured above to
   avoid the floor entirely in both engines. It is the largest change of the
   three and it reaches 046's rule, 056's iOS branch and the drag preview's
   matching constant, all of which are written in terms of ``zoom`` today, and
   a transform does not reflow -- so the sheet's layout at 50 % would have to
   be checked, on paper as well as on screen. Not to be taken without the
   printing check that 046 and 047 both turned on.

What is left
============

For whoever has the iPad, and it is one measurement rather than a change:

* Open the label editor on the tablet, on a label whose name is long enough to
  be fitted well under 18px, and read the computed ``font-size`` of its ``h1``
  in Safari's Web Inspector against the inline one the element carries. Equal
  means iOS Safari has no such floor and option 1 closes this. Larger means it
  does, and the ruling is between 2 and 3.
* 056 lists a Safari debugging setup for the tablet as being put together
  outside this repository; this measurement is one more thing for the same
  session, and it is the same computed-``font-size`` reading its own item 2
  wants.

See also
========

* :doc:`061-every-safari-claim-was-verified-in-a-non-safari-engine` -- the work
  that produced this measurement.
* :doc:`046-the-label-editor-opens-at-print-size` -- where the ``zoom`` came
  from.
