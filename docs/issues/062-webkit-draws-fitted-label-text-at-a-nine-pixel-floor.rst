===============================================================
Issue 062: WebKit draws fitted label text at a nine-pixel floor
===============================================================

:Status: Rejected
:Severity: Medium
:Area: templates / labels UI
:Reported: 2026-08-02
:Source: Measured while running the browser suite in WebKit for the first time
    (issue 061)
:Evidence: ``browser_tests/test_label_editor.py`` --
    ``test_a_fitted_name_is_drawn_at_the_size_it_was_fitted_to`` pins what each
    engine does: in Chromium the drawn size equals the inline size fitty wrote,
    in WebKit it is strictly larger. It stays, and it is what will notice if
    the floor ever moves in either engine. The sweep behind it is in "Measured"
    below
:Depends on: (none)
:Blocks: (none)
:Related: 046 -- the ``zoom: 0.5`` this is entirely a consequence of
    056 -- the same page, the same symptom family, and the report that says
    Safari's measurements are the load-bearing question
    045 -- the tablet the symptom was reported from
    061 -- the engine parametrisation that found this
:Decision: Option 1 -- change nothing until the device says so -- and then the
    device said so. The maintainer was asked which of the three options to take
    and, with it, "how small may a species name be drawn on the sheet?", and
    answered both: wait for the iPad, and 18px. Option 2 had been built before
    those answers arrived, on the evidence and against this file's own ranking,
    and it was withdrawn to obey the ruling. The wait then ended the way option
    1 said it might: on 2026-08-04 the maintainer reported from the tablet that
    every species title on the sheet looks right in iOS Safari. That is the
    condition option 1 was waiting on -- "if iOS Safari has no such floor there
    is nothing here to repair" -- so this is rejected rather than deferred. The
    18px answer is not discarded: it is the product question settled, and it is
    the number to use if this is ever reopened. See "Why this is Rejected and
    not Fixed" for what the report does and does not establish
:Resolution: Rejected on the device report of 2026-08-04, recorded in
    "Why this is Rejected and not Fixed": no user-visible defect on the machine
    every report about this page came from, so there is nothing to repair. No
    code changed. The option-2 implementation, green in both engines, is kept
    on the tag ``interim-062-option-2`` (commit ``55ce0a8``) and costed out
    below, so reopening this is a cherry-pick rather than an investigation

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

**The "up to twice" in "Problem" was wrong**, and working on this is what found
it. The window where the floor bites is 9px to 18px, but nothing on this page
was ever fitted below **16px**: that is fitty's own default ``minSize``, which
``fitTextToSpace`` never overrode, so the 16px in "Measured" is not a fit at
all -- it is the clamp fitty had already applied. The real exposure was
therefore the two pixels between 16 and 18, a name drawn 12.5 % too large, and
never more. That makes this smaller than it was filed as -- which is part of
why waiting for the device costs little -- and it makes option 2 smaller too:
a floor is already there, with a number in it that was never chosen for this
page.

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

**Option 1: change nothing until the device says so.** The maintainer was asked
which option to take and how small a name may be drawn, and answered both. The
second answer -- 18px, the floor -- settles the product question for whoever
implements this; it was not an instruction to implement it then, and this file
did not treat it as one.

The wait was short: the device answered two days later and answered against
doing anything, which is "Why this is Rejected and not Fixed" below. So option
1 was not only the ruling, it was the right ruling -- the evidence this file
was built on came from an engine standing in for a device, and the device did
not agree that anything was wrong. What that cost was a day's work withdrawn;
what it bought was not shipping a change to a printed artefact nobody needed.
That is a trade worth remembering the next time a measurement here disagrees
with a machine nothing here can reach.

How that ruling was arrived at is worth recording, because it was got wrong
first. The option answer named the second of three cards, and the cards were
not in the options' numeric order -- the question put the recommendation first,
so card 2 was labelled "Option 1: wait for the iPad". It was read as option 2,
which agreed with what had already been built, and the file argued for that
reading from the other answer: option 1 changes nothing, and a sheet nothing
changed on has no 18px minimum to set. That argument was reasonable and it was
wrong. What settled it was asking again with two cards whose labels carried no
numbers at all -- "floor the fit, as committed" against "change nothing until
the iPad" -- and saying in the question that the second answer meant reverting.
The answer was the same as the first time. **Two answers agreeing beat one
inference from what a third answer implies**, and the numbering that made the
first one ambiguous was this file's fault, not the reader's.

What option 2 costs, measured rather than estimated
---------------------------------------------------

It was built and run in both engines before the ruling came, and then withdrawn.
None of it is in the tree. It is kept two ways so that taking option 2 later is
a cherry-pick and not an investigation: as the tag ``interim-062-option-2``
(commit ``55ce0a8``, on no branch), and as this list, which is the part that
survives whatever happens to the tag.

* it is **one argument**. ``fitTextToSpace``'s desktop branch becomes
  ``fitty(el, {maxSize: fontSize, minSize: MIN_DRAWN_FONT_SIZE /
  screenScale()})`` -- nine drawn pixels expressed in the sheet's own
  coordinates, which is 18 specified at 046's 50 %, and which follows
  ``--screen-scale`` if 046 ever moves it;
* **the wrap is free.** Option 2 asks that a name which still does not fit be
  handled deliberately. fitty already does it: it switches ``white-space``
  from ``nowrap`` to ``normal`` exactly when it lands on ``minSize``. No new
  code, and the behaviour is not new either -- see the correction in "Why it
  matters";
* **the iPad branch must not be clamped**, and this is the part that would
  have cost a day to find later. That branch writes the screen size itself
  rather than a print size the ``zoom`` shrinks, and WebKit's minimum exempts
  text already below it -- 4px and 8px are drawn untouched in the sweep above.
  Clamping it made the label's text stop following the label's width, and
  ``test_ipad_label_text_keeps_the_result_after_fit_observer_is_removed``
  failed in both engines. That test is 056's and it is right;
* **nothing else in the suite moves.** With the floor on the desktop branch
  only, the browser suite was green in both engines (59 passed, 7 skipped) and
  the Python suite was green (471 passed);
* **printing is unaffected in the direction that would matter.** The fitted
  size is the printed size -- the ``zoom`` is ``@media screen`` only -- so the
  floor is also the smallest a name prints, 18px, about 13.5pt on a 14 cm
  label. That is larger than what prints today, never smaller, because 16px is
  already the smallest fitty will produce. So option 2 needs no print check,
  unlike option 3.

Only the test changes with it: ``test_a_fitted_name_is_drawn_at_the_size_it_was
_fitted_to`` asserts a different thing per engine today, and under option 2 it
asserts the one thing both must agree on, that the fit lands on the floor, and
that the name wraps there.

Why this is Rejected and not Fixed
==================================

On 2026-08-04 the maintainer looked at the label editor on the iPad and
reported that every species title on the sheet looks right in iOS Safari. That
ends the wait option 1 imposed, and it ends it on the side that repairs
nothing: the sheet is correct on the machine every report about this page came
from, so there is no defect here to fix.

**What the report establishes**, and it is the thing that matters: no gardener
is looking at an overflowing label. That was the whole of "Why it matters", and
it is the symptom 045 and 056 were reported as.

**What it does not establish**, said plainly so that nobody later reads this
file as having measured something it did not:

* it is a look, not the Web Inspector reading this file asked for -- computed
  ``font-size`` against the size the element carries. So it does not say
  whether iOS Safari applies the floor; it says that if it does, nothing
  visible follows;
* and the two are easy to confuse here, because the effect is small. The
  exposure is 12.5 % -- see "Why it matters" -- and only on a name long enough
  to be fitted below 18px in the first place. A sheet of ordinary Finnish
  species names may simply never reach that, in which case "looks right" is
  what both answers would look like.

Neither reservation changes the decision. An issue exists to describe something
wrong with the product, and the product is not wrong; a floor that produces no
visible effect is a fact about WebKit, and this file is where it is written
down. The cost of being wrong is also known rather than guessed: reopening is
the tag ``interim-062-option-2``, one ``minSize`` argument, and the test
change described above.

If it is ever reopened
----------------------

Two triggers, and the second is cheaper than it looks:

* a report of a label whose name does not fit -- the same symptom family as 045
  and 056. Then take the reading below before taking the change, because a name
  that overflows at 18px is a different defect from one that overflows because
  it was drawn at 18px when it was fitted to 16;
* the reading itself, if anyone is in Safari's Web Inspector on the tablet for
  another reason: computed ``font-size`` of a fitted ``h1`` against the
  ``--fit-screen-size`` it carries, on a label whose name is long enough to be
  fitted small. Equal means the floor is Playwright's WebKit and not Safari,
  and this file's central measurement is about a test engine rather than a
  device -- worth knowing, since 061 rests on that engine standing in for this
  one. 056 lists a Safari debugging setup for the tablet being put together
  outside this repository, and this is one more reading for that session.

See also
========

* :doc:`061-every-safari-claim-was-verified-in-a-non-safari-engine` -- the work
  that produced this measurement.
* :doc:`046-the-label-editor-opens-at-print-size` -- where the ``zoom`` came
  from.
