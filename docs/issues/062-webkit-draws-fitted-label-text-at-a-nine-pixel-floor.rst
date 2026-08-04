===============================================================
Issue 062: WebKit draws fitted label text at a nine-pixel floor
===============================================================

:Status: Fixed
:Severity: Medium
:Area: templates / labels UI
:Reported: 2026-08-02
:Source: Measured while running the browser suite in WebKit for the first time
    (issue 061)
:Evidence: ``browser_tests/test_label_editor.py`` --
    ``test_a_fitted_name_is_drawn_at_the_size_it_was_fitted_to``. It pinned
    what each engine did before the fix -- in Chromium the drawn size equalled
    the inline size fitty wrote, in WebKit it was strictly larger -- and now
    asserts the one thing both engines have to agree on: the name is drawn at
    the size it was fitted to. The sweep behind it is in "Measured" below
:Depends on: (none -- it was measurable and reproducible here, and the ruling
    it waited for is in ``Decision``)
:Blocks: (none)
:Related: 046 -- the ``zoom: 0.5`` this is entirely a consequence of
    056 -- the same page, the same symptom family, and the report that says
    Safari's measurements are the load-bearing question
    045 -- the tablet the symptom was reported from
    061 -- the engine parametrisation that found this
:Decision: Option 2 -- never fit below the floor. The question put to the
    maintainer was which of the three options to take, and with it the product
    question the ruling wanted: "how small may a species name be drawn on the
    sheet?", offering the floor itself, 20px and 24px. It was asked twice and
    did not get through -- the ask was refused by the harness both times, so
    this is a question that was never delivered rather than one that went
    unanswered, and either way the rule is the same: rule on the evidence and
    write down what was asked (see "The ruling"). Option 1 is not safe: the floor is reproducible in
    Safari's own engine on this machine, and the reading that would clear it is
    on a tablet nothing here can reach. Option 3 is not this issue's to take:
    it would need a print-layout check no engine here can do, and it is
    available unchanged if the maintainer later wants it. The minimum is the
    floor itself -- nine drawn pixels, 18 specified -- because that is the
    smallest size the two engines agree on, and choosing anything larger is a
    legibility judgement nobody here is entitled to make
:Resolution: 64bd4e3 -- ``fitTextToSpace`` fits no smaller than
    ``MIN_DRAWN_FONT_SIZE / screenScale()``, and a name that does not fit at
    that size wraps

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
not fit. (That last clause is this report's own arithmetic and it overstates
the exposure -- fitty was never asked for anything below 16px. "Why it matters"
carries the correction, which fixing this is what found.)

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
applies the floor the name is drawn larger than the size that was computed to
make it fit, so it can overflow the label it was fitted into -- which is what a
gardener sees, and it is the family of symptom 045 and 056 were both reported
as. On this data the effect is 16px drawn at 18px.

**The "up to twice" in "Problem" was wrong**, and fixing this is what found
it. The window where the floor bites is 9px to 18px, but nothing on this page
was ever fitted below **16px**: that is fitty's own default ``minSize``, which
``fitTextToSpace`` never overrode, so the 16px in "Measured" is not a fit at
all -- it is the clamp fitty had already applied. The real exposure was
therefore the two pixels between 16 and 18, a name drawn 12.5 % too large, and
never more. That makes this smaller than it was filed as, and it makes the fix
smaller too: the floor was already there and had the wrong value in it.

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

The ruling
==========

Option 2 was taken, with the minimum set to the floor itself. The question that
would have decided it -- which option, and how small a name may be drawn -- was
put to the maintainer twice and did not reach them; ``Decision`` above records
it and the reasoning that settled it without an answer.

What the change is, in ``fitTextToSpace``:

* the desktop branch hands fitty ``minSize: MIN_DRAWN_FONT_SIZE /
  screenScale()`` -- nine drawn pixels expressed in the sheet's own
  coordinates, which is 18 specified pixels at 046's 50 %. If 046's scale ever
  moves, the floor moves with it rather than going stale;
* the iPad branch is **deliberately not** floored, and the measurements above
  are why. That branch does not write a print size for the ``zoom`` to shrink;
  it writes the screen size itself, and WebKit's minimum exempts text whose
  own size is already below it -- 4px and 8px are drawn at 4px and 8px in the
  sweep. So there is nothing there for a floor to prevent, and adding one has
  a cost that was measured rather than argued: clamped, the label's text
  stopped following the label's width, and
  ``test_ipad_label_text_keeps_the_result_after_fit_observer_is_removed``
  failed in both engines. That test is 056's, and it is right;
* a name that does not fit at the floor **wraps**. That is option 2's "handled
  deliberately", and it needed no new code: fitty already switches
  ``white-space`` from ``nowrap`` to ``normal`` exactly when it lands on
  ``minSize``. Wrapping is what happened before this change too, at 16px
  instead of 18px -- so nothing about a very long name is new except two
  pixels.

What it costs on paper: the fitted size is the printed size -- the ``zoom`` is
``@media screen`` only -- so the floor is also the smallest a name is printed,
18px, about 13.5pt on a 14 cm label. That is *larger* than what printed before,
never smaller, because 16px was already the smallest fitty would produce. So
this change cannot shrink anything on paper, and the printing check option 3
would have needed is not needed here.

What is left
============

For whoever has the iPad, and it is one measurement rather than a change. The
fix does not depend on it -- flooring the fit is right in either answer, since
Chromium and WebKit now draw the same sheet either way -- but it is what says
whether the *symptom* was ever visible on the device:

* Open the label editor on the tablet, on a label whose name is long enough to
  be fitted small, and read the computed ``font-size`` of its ``h1`` in
  Safari's Web Inspector against the ``--fit-screen-size`` the element carries
  -- the device takes the branch that writes that property, not fitty's.
  Equal is the answer this fix expects, and means the exemption above holds on
  the device as it does here. Larger means iOS Safari floors that branch too,
  and then the iPad branch wants the clamp this change deliberately left out
  of it, together with something better than a clamp for
  ``test_ipad_label_text_keeps_the_result_after_fit_observer_is_removed``,
  which is the test that says a label's text follows its width.
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
