==========================================================================
Issue 056: iPad label text is doubled, and grows until it vanishes
==========================================================================

:Status: Accepted
:Severity: Medium
:Area: templates / mobile
:Reported: 2026-07-31
:Source: Maintainer report from the iPad, ``docs/issues/incoming.rst``, while
    looking at 045's cheap half
:Evidence: ``browser_tests/test_label_editor.py`` --
    ``test_a_label_whose_photo_never_loads_still_fits_its_text`` and
    ``test_the_ipad_fits_a_label_whose_photo_never_loads`` pin the first half
    on the desktop and on the iPad branch respectively, and
    ``test_ipad_label_text_keeps_the_result_after_fit_observer_is_removed``
    pins that the iPad branch is not handed to fitty and does not move on a
    resize. All three fail against the template as it was before 746ce71 and
    pass after it. The second half has no test and cannot have one here: see
    "What emulation cannot see"
:Depends on: (none -- 017's browser suite is what makes the first half
    testable at all, and it is ``Fixed``)
:Blocks: (none)
:Related: 045 -- the same tablet, the same template, and the report this one
    was noticed inside
    046 -- the ``zoom: 0.5`` this issue's arithmetic is entirely about
    047 -- the same page's print toggle
    017 -- the browser suite that carries the evidence below
    048 -- where the photos come from, which is the question this report parks
    039 -- the per-label photo choice, whose chevrons re-fit a label
:Decision: Ruled on 2026-08-01 on the evidence, not by the maintainer: the
    first half is fixed by 746ce71 and is now pinned by three browser tests
    that go red without it, so nothing is left to decide there. The second
    half stays open and this issue stays actionable, because the change 746ce71
    makes for it -- one-shot fitting and separate screen and print sizes on
    iOS -- runs on the device and nowhere else, and nothing available here can
    tell whether the growth stopped. It is deliberately **not** marked
    ``Fixed`` on the strength of the commit message: the register's rule is
    that a status says what was established, and what was established is one
    half. The remaining work is a look at the tablet, not a change to the
    template, and it is written out under "What is left". The photo question
    this report parks is answered under "Why do the photos fail at all?" and is
    **not** filed as its own issue, because no defect in this repository could
    be demonstrated for it
:Resolution: (none yet) -- the first half is fixed in 746ce71 "fix(labels): fit
    text in iPad Safari", which this issue does not close, and the second half
    has no resolution until the device says so

Problem
=======

As reported from the iPad (7th generation, iPadOS 18.7.9, Safari) on
2026-07-31, on ``/kasvimuseo/planting-labels/``:

**Label text is about twice the size it should be, and on the labels whose
photo loads it grows until it disappears.**

Two symptoms, split by whether the photo arrives:

* on the majority of labels, where it does not, the text is simply too big and
  stays that way;
* on the seven top labels where it does, the text starts at that same doubled
  size, grows every few seconds, and eventually vanishes.

The report traced the first half to one line of control flow and left the
second one suspected but not reproduced. This file keeps both traces, adds what
the browser suite now measures, and says which of the two the fix that has
since landed can be held to.

The first half: no photo, no fit
================================

``kasvimuseo/templates/kasvimuseo/reports/planting-labels.html`` fits the
species name and the classification line to the label with fitty. Before
746ce71 the only thing that ever called ``fitTextToSpace`` was the
``verticalPhotoWidth`` watcher on the ``name`` and ``classification``
components. That property changes in one place, ``setAspect``, which is the
``photo`` component's ``@load`` handler. **No photo, no fit**: the text kept the
declared ``30pt`` / ``24pt``, and on a label drawn at 046's ``zoom: 0.5`` that
is about double what a fitted label shows.

Measured in the browser suite, against the template as it was before 746ce71,
with the seeded names replaced by one long enough to need fitting and every
``/media/`` request failed::

    desktop, no photo   40px, 40px      (the declared 30pt, never changed)
    iPad branch         40px, 40px
    desktop, photos     16px, 16px

Two and a half times, on this data. The report's own headless reproduction said
the same thing in the same units: with half the labels' photos 404ing, every
one of them reported ``font-size: 40px`` and never changed.

The same measurement after 746ce71::

    desktop, no photo   16px, 16px      (fitted, exactly as with a photo)
    desktop, photos     16px, 16px

``fitMixin`` gained a ``mounted`` hook that fits on the next tick whatever the
photo does -- "Fit even when the photo is unavailable: the photo load is not a
reliable signal that the label itself is ready" -- and the two watchers now
re-fit after a tick rather than during the same one. That is exactly the cause
above, removed, and it is pinned by
``test_a_label_whose_photo_never_loads_still_fits_its_text``.

The second half: it grows, and then it is gone
==============================================

Not reproduced anywhere but on the device, then or now.

The report tested one suspect and cleared it: fitty measuring inside 046's
``zoom: 0.5`` returns the same font size as without it (22.69px against 22.67px
in WebKit, 24.23 against 24.18 in Chromium, unchanged over three passes), so
the zoom is not corrupting fitty's arithmetic in an emulated engine. **Do not
re-test that.** What it left to suspect was iOS text autosizing
(``-webkit-text-size-adjust``, which this page gets only from the CDN copy of
sanitize.css) and fitty's own resize observers on the device.

746ce71 addresses the second suspect and, if its premise is right, the first
one too. On iOS -- and only there -- the template now:

* measures a clone of the text in a ``position: fixed`` wrapper outside the
  zoomed subtree, with ``-webkit-text-size-adjust: none`` on it, and fits once;
* writes the result into ``--fit-screen-size`` and ``--fit-print-size`` instead
  of an inline ``font-size``, which a new ``@supports (-webkit-touch-callout:
  none)`` block reads for screen and for print separately;
* never subscribes to fitty at all, so there is no resize observer to fire
  repeatedly -- "iPad Safari sends layout notifications while applying CSS
  zoom, though, and fitty then repeatedly grows the same label".

Its premise is stated in the commit message and in the code comments: that
Safari applies ``zoom`` to the label geometry but reports text and width
measurements in a coordinate system that does not match, dividing computed
values inside the zoom by the zoom factor. That is a claim about one browser on
one device, and it is the load-bearing part of the whole iOS branch.

What emulation cannot see
=========================

The browser suite runs Playwright's Chromium against a real gunicorn-served
instance (issue 017), and the fixtures emulate the device as far as a viewport,
a touch screen and a user agent go. Three things about this fix are outside
what that can reach, and they are why this issue is ``Accepted`` and not
``Fixed``:

* **The CSS half never applies.** The iOS rules are behind ``@supports
  (-webkit-touch-callout: none)``, the standard iOS-Safari-only test.
  ``CSS.supports('-webkit-touch-callout', 'none')`` is ``false`` in *both*
  Playwright engines on this host -- Chromium and WebKit alike, measured -- so
  no browser here draws a label at ``--fit-screen-size``. The tests check those
  two custom properties where they are written, not where they are drawn.
* **The premise cannot be checked.** In both engines ``getComputedStyle``
  inside the ``zoom: 0.5`` subtree reports the declared ``40px``, not the
  doubled value the fix compensates for. So the emulated engines are the case
  the commit says is *not* the problem, and the arithmetic that matters runs
  only where nothing here can watch it.
* **The growth was never reproduced.** There is nothing to hold a fix against.
  ``test_ipad_label_text_keeps_the_result_after_fit_observer_is_removed``
  asserts that the iPad branch is never handed to fitty and that twelve
  ``resize`` events do not move the fitted size, which is the *mechanism* the
  commit removes; it cannot show that the mechanism was the cause.

This is the same discipline 045 wrote down: its cheap half was measured in
headless WebKit and Chromium and its file lists what still wants the device,
rather than asserting the device agrees.

Why do the photos fail at all?
==============================

The report parks this, and it is the right question -- it was the trigger for
the first half, and a serving problem would have been the more useful thing to
fix first. What can be established here:

* **The page builds photo URLs from ``photo.get_display_url()``**
  (``kasvimuseo/photos.py``), so every label photo is a photologue derived size
  under ``MEDIA_URL`` + ``photologue/photos/cache/``. Photologue generates a
  derived size on first access, which needs the *original* file in the local
  ``MEDIA_ROOT``; where the original is absent it returns quietly and the URL
  still names the cache path.
* **Since 048 that URL is this server's own** ``/media/``, and
  ``ylaneenkasvit.media.serve_media`` serves what is on disk and redirects the
  rest to ``MEDIA_FALLBACK_URL`` -- the public production media host. So a
  photo the development machine does not have is a ``302`` the *browser* has to
  follow to the public internet, which is 048's "no offline development"
  impact, restated for a tablet.
* **On a checkout that has run** ``dev/kasvimuseo media fetch`` **nothing
  should fail.** On the checkout these notes were written on, all 137
  originals the production dump references are present in ``media/`` and 139
  derived ``_display`` files have been generated beside them, so every URL the
  editor asks for is answered locally with a 200.

Two candidates remain for the tablet, and both are about the machine the server
runs on rather than about this repository:

1. **That machine has not fetched the media**, so every photo is a redirect to
   the public host and the failures are whatever the tablet's route to it is.
2. **That machine has a** ``local_settings.py`` **that predates 048**, in which
   case ``MEDIA_URL`` is still ``//media.kasvit.ambitone.com/`` and no photo is
   served locally at all. ``dev/kasvimuseo`` prints a note when it finds such a
   file, which is easy to miss in a page of gunicorn output.

Neither is a defect that can be demonstrated from here, and one look at the
tablet's network inspector or the development server's access log distinguishes
them, so **this is not filed as its own issue**. What has changed since the
report is that it is no longer load-bearing: after 746ce71 a label is fitted
whether or not its photo arrives, so a failing photo costs a picture and not
the text.

What is left
============

For whoever has the iPad. All of it is looking, not changing:

1. **Open the label editor on the tablet** and read the species name on a label
   whose photo did not load. It should be the same size as one whose photo did.
   That is the first half, and it is the one this file claims is fixed.
2. **Watch a label whose photo did load** for a minute. If the text still grows
   every few seconds, the second half is not fixed and the suspect list above
   is where to start -- with ``-webkit-text-size-adjust`` first, since the fix
   sets it on the measuring clone only.
3. **Print one sheet** and check the text is the printed size rather than the
   screen size. The iOS branch keeps the two apart in ``--fit-print-size`` and
   ``--fit-screen-size``, and no engine here applies either.
4. **If the text is now too small rather than too large**, say so: in emulation
   the iOS branch fits to a clone measured at 506px where the desktop path fits
   inside the zoomed box, and the two disagree by about a sixth on the same
   label. Which is right depends on the coordinate system the device actually
   reports, which is the premise above.
5. **Answer the photo question while the tablet is out**: whether a label photo
   is a local 200 or a redirect to ``media.kasvit.ambitone.com``.

If 1 and 2 hold, this becomes ``Fixed`` with 746ce71 in ``Resolution`` and
nothing else changes.

The report added one note about how to do 2 and 4 with more than eyes: an iPad
Safari debugging setup is being put together outside this repository, in
``~/repos/nixos-config`` and a task of its own, and having it before touching
the second half is worth the wait. Safari's Web Inspector attached to the
tablet is the only thing that can show the computed ``font-size`` growing,
which is the measurement this file could not take.

Traps found on the way
======================

* **A test that passes on the broken code.**
  ``test_label_text_fits_and_stays_stable_during_layout_passes``, added by
  746ce71, passes against the template as it was before 746ce71. It is a real
  test -- it says fitty does not run away on a desktop over twelve resize
  passes -- but it is not a regression test for either half of this report,
  because the label it measures has a photo and is therefore fitted by the old
  watcher too. The two tests named in ``Evidence`` above were added for that
  reason: both fail before the fix.
* **The iPad was emulated as a desktop.** 746ce71's own iPad test redefined
  ``navigator.platform`` and ``navigator.maxTouchPoints`` on a 1280x900 mouse
  page. It now runs on ``ipad_page`` -- the iPad viewport, a touch screen and
  the device's user agent -- which is the fixture the register asked for in
  045. The user agent is deliberately kept off the shared ``touch_page``: it
  would put every touch test on a code path whose CSS half no engine here can
  apply.
* **``@supports (-webkit-touch-callout: none)`` is not a WebKit test.** It was
  worth checking that Playwright's WebKit could stand in for Safari here, and
  it cannot: the property is an iOS thing rather than an engine thing, and the
  Linux WebKit build answers ``false`` exactly as Chromium does.
