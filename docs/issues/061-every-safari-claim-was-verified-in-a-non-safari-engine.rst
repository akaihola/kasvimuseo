=====================================================================
Issue 061: Every Safari claim in the register was checked in Chromium
=====================================================================

:Status: Fixed
:Severity: Medium
:Area: tests / browser engines
:Reported: 2026-08-02
:Source: Reading ``browser_tests/conftest.py`` next to the four iPad reports it
    is cited by
:Evidence: The suite itself, now parametrised: every test in
    ``browser_tests/`` runs once per engine and is named after the one it ran
    in. ``dev/kasvimuseo app browser-test --engine webkit`` is green -- 24
    passed, 6 skipped -- and ``--engine chromium`` is green with 30 passed, so
    the two engines agree on every assertion either can reach. The measurements
    they do **not** agree on are in "What WebKit said" below; one of them is
    filed as 062 and pinned by a test of its own,
    ``test_a_fitted_name_is_drawn_at_the_size_it_was_fitted_to``
:Depends on: (none -- 017's browser suite is what there is to parametrise, and
    it is ``Fixed``)
:Blocks: (none)
:Related: 017 -- the suite this changes, and the issue that chose Chromium
    045 -- the iPad drag work, whose own file says the touch drag cannot be
    expressed against WebKit
    046 -- the ``zoom: 0.5`` that turns out to be where the engines differ
    047 -- the same page's print toggle, reported from the same tablet
    056 -- the iPad fitter, whose load-bearing premise is about Safari
    062 -- the one product finding this work produced
:Decision: Ruled on the evidence rather than by the maintainer, because what
    it asks for is a test arrangement rather than a change to the application.
    Three rulings. **One: both engines by default.** A single-engine run stays
    one command (``--engine webkit`` or ``KASVIMUSEO_BROWSER_ENGINES``), but
    the default has to be both, because the failure this exists to catch is
    exactly the one nobody would go looking for. **Two: two CI jobs, not
    one.** The matrix leg names the engine in the red light, which is the whole
    information content of the finding; the price is a second image build, and
    the legs run in parallel so the wall clock of a run does not move.
    **Three: the whole suite in both, not a mobile-only subset.** Splitting it
    -- everything in Chromium, the iPad tests in WebKit -- saves about a minute
    of runner time and gives up most of what the split is for, since the
    engines differ in layout and text measurement and those are the tests that
    would have stayed Chromium-only
:Resolution: 924bd84 "test(browser): run the suite in WebKit as well as
    Chromium": ``browser_tests/conftest.py`` launches either engine,
    ``dev/kasvimuseo app browser-test`` runs both, and
    ``.github/workflows/tests.yml`` runs one per matrix leg. The finding the
    WebKit run produced is 062, filed rather than fixed here

Problem
=======

``browser_tests/conftest.py`` launched ``playwright.chromium`` and nothing
else, so **every** browser test in this repository ran in Chromium -- including
the ones that emulate the iPad with ``has_touch``, ``is_mobile``, an iPad
viewport and the device's user agent.

The defects those tests were written for are Safari defects. 045, 046, 047 and
056 are all iPad reports; 056 is ``Accepted`` rather than ``Fixed`` precisely
because the change it verifies runs on the device and nowhere else, and the
commit it verifies (746ce71) states its premise as a claim about *Safari*
applying CSS ``zoom`` to label geometry while reporting text and width
measurements in a coordinate system that does not match.

Emulating an iPad in Chromium reproduces the layout box and the touch events.
It cannot reproduce WebKit's measurement behaviour, which is what every one of
those four issues is actually about. The suite was therefore stating, for four
mobile-Safari reports, that a fix works -- in the one engine none of them was
reported from.

Playwright ships WebKit. It is not Safari: it is Safari's engine on this
platform, with none of iOS around it, which is why ``@supports
(-webkit-touch-callout: none)`` is false in it exactly as it is in Chromium
(056 measured that and it is unchanged). What it does share with Safari is the
arithmetic -- how text is measured, and what ``getComputedStyle`` reports
inside a ``zoom``. That is the part these reports turn on, and it cost one
parameter to start using.

What changed
============

* ``browser_tests/conftest.py`` takes ``--engine`` (repeatable) or
  ``KASVIMUSEO_BROWSER_ENGINES``, defaulting to both, and parametrises every
  test over it at session scope, so each engine is launched once per run and
  the test id says which one it was: ``test_a_tap_on_a_number_moves_nothing``
  became ``test_a_tap_on_a_number_moves_nothing[webkit]``.
* ``dev/kasvimuseo app browser-test`` therefore runs both engines and needs no
  new flag of its own; the pytest arguments it already passes through are how
  a run is narrowed.
* ``.github/workflows/tests.yml``'s ``browser`` job became a two-leg matrix,
  ``playwright (chromium)`` and ``playwright (webkit)``, each installing only
  its own engine, with ``fail-fast: false`` so one engine's failure does not
  cancel the other's run.
* ``README.rst`` documents the single-engine run and what WebKit is and is not.

What WebKit said
================

**Everything it can run, it passes.** 24 of the 30 tests, including every
assertion 045, 046, 047 and 056 rest on: the fitter runs without a photo, the
iOS branch writes ``--fit-screen-size`` and ``--fit-print-size`` and is never
handed to fitty, the mouse drag regroups the sheet, the save cycle round-trips,
the staff gate answers 403, the truncated response is refused, and both
Grappelli changelist controls work. Nothing WebKit contradicts is asserted
anywhere in this register.

Two measurements the engines do **not** agree on, neither of which any
assertion in the suite is tight enough to notice:

A long name, no photo, at 50 % zoom:

===================================== ========== ==========
Measurement                           Chromium   WebKit
===================================== ========== ==========
Species name, inline size fitty wrote 16px       16px
Species name, ``getComputedStyle``    16px       **18px**
Species name, drawn height            17.59px    19.80px
iOS branch, ``--fit-screen-size``     6.645px    5.953px
iOS branch, ``--fit-print-size``      13.290px   11.905px
Label ``offsetWidth``                 529        530
===================================== ========== ==========

The first is a floor WebKit applies to text inside issue 046's ``zoom: 0.5``,
and it means the size fitty computes is not the size that is drawn. It is a
product finding rather than a test one, so it is **062** and not fixed here.

The second is the two engines disagreeing by about a tenth about the iOS
branch's own arithmetic on the same page at the same metrics. Both satisfy
``test_the_ipad_fits_a_label_whose_photo_never_loads``, which asks for "under
20px", and the ratio the same test pins -- print exactly twice screen -- holds
in both. It is recorded here because 056's item 4 asks whether that branch fits
*too small* on the device, and this says the answer depends on the engine
before it depends on the device.

The six tests WebKit cannot run
===============================

All six are touch drags, and all six skip with the reason named where it
happens, in ``touch_drag``:

* ``test_a_number_moves_between_labels_by_touch``
* ``test_a_touch_gesture_the_system_takes_away_changes_nothing``
* ``test_the_dragged_number_follows_the_finger``
* ``test_the_drag_preview_is_drawn_only_over_the_empty_sheet``
* ``test_the_drag_preview_follows_the_finger_at_the_screen_zoom``
* ``test_saving_after_a_touch_drag_persists_the_new_arrangement``

A touch drag is dispatched over ``Input.dispatchTouchEvent``, a Chrome DevTools
Protocol call, so that the browser does its own hit-testing, applies
``touch-action`` and generates the pointer events itself. WebKit speaks no CDP,
and Playwright's synchronous ``touchscreen`` can only tap. 045 wrote that down
when the drag was written and it is still true; the alternative -- constructing
``TouchEvent`` objects in JavaScript -- removes the browser from the part of the
test that is worth having, so the test skips rather than pretending. The three
touch tests that only tap (``test_a_tap_on_a_number_moves_nothing`` among them)
run in both engines.

Everything else WebKit runs. Nothing was fixed as a Chromium-specific test
assertion, because no test turned out to have one.

What it costs
=============

Measured in this checkout on an otherwise idle machine. Every test reseeds the
database first, so about a second of each run is not a browser at all:

======================================== ============ ==========
Run                                       Tests        Wall clock
======================================== ============ ==========
``--engine chromium``                     30 passed    1 min 46 s
``--engine webkit``                       24 + 6 skip  2 min 23 s
Both, one pytest run                      54 + 6 skip  4 min 32 s
======================================== ============ ==========

WebKit is the slower engine here by about a third, and the six it skips still
pay for their fixtures, which is a reseed and a login each. Under load the same
runs took half again as long, so these are the floor rather than a promise.

On CI the ``browser`` job was about two and a half minutes -- image, browser,
suite. It is now two jobs of roughly that each, in parallel: **the wall clock
of a whole workflow run is unchanged**, and the runner minutes this job spends
roughly double, from about 2.5 to about 5. That is the price, and it is
argued for in ``Decision`` above and repeated in the workflow's own comments,
where somebody changing the job will read it.

What emulation still cannot see
===============================

Unchanged by this work, and worth not re-testing:

* **iOS is not WebKit.** ``@supports (-webkit-touch-callout: none)``, the test
  the iOS branch of the template hides behind, is false in Playwright's WebKit
  as it is in Chromium -- 056 measured it and this run agrees. The CSS half of
  056's fix still cannot be drawn anywhere here.
* **A touch drag on the engine that matters** is still unavailable, so the one
  thing 045 wanted the device for is still wanted from the device.
* **Neither engine is the tablet.** WebKit narrows the gap to the engine; it
  does not close the gap to the machine.

Traps found on the way
======================

* **A session-scoped fixture parametrised from the command line.** The engine
  list is not known when the ``browser`` fixture is defined, so it is
  parametrised in ``pytest_generate_tests`` with ``scope='session'``. Without
  that scope pytest launches a browser per test; with it, the tests are
  reordered into one group per engine, which is why an engine's failures
  arrive together.
* **A test that failed once, in Chromium, under memory pressure.**
  ``test_the_dragged_number_follows_the_finger`` compared a 25.87px dragged
  number against a 16.97px source and failed its ``rel=0.5`` bound, in the one
  run whose gunicorn container was killed by the host a few minutes later. It
  has passed in every run since, in both engines. Recorded because the next
  person to see it should suspect the machine before the template.
* **The suite is slower than the sum of its assertions.** Every test reseeds
  the database, so a run costs about a second per test before a browser does
  anything. That is the number that doubles with a second engine, and it is
  worth knowing before anybody adds a third.

See also
========

* :doc:`017-browser-suite-unrunnable-vue-editor-untested` -- where
  ``browser_tests/`` came from.
* :doc:`062-webkit-draws-fitted-label-text-at-a-nine-pixel-floor` -- the one
  product finding this work produced.
* :doc:`056-ipad-label-text-is-doubled-and-grows-until-it-vanishes` -- the
  report whose premise is about Safari's measurements.
