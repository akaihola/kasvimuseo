================================================================================
Issue 017: Browser test suite is unrunnable, so the Vue label editor is untested
================================================================================

:Status: Fixed
:Severity: High
:Area: tests / gap
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: browser_tests/test_label_editor.py -- eleven tests that drive the
    editor in Chromium against the real application. Replaces
    ``integration_tests/``, which is deleted.
:Depends on: (none)
:Blocks: (none)
:Related: 018 -- both are about whether tests are run at all
    010, 039 -- label editor behaviour that neither covers
    013 -- the FIXMEs a browser test would settle
    045, 046, 047 -- label editor and tablet behaviour no test can see
:Decision: Ruled by the maintainer on 2026-07-31: **rebuild it on the host**, a
    third shape neither option in "Options" below named. ``integration_tests/``
    is deleted; ``browser_tests/`` is Python 3 on the host, driving Playwright
    against the real application in its own container, run by
    ``dev/kasvimuseo app browser-test`` and by a third CI job. Option 1 was
    rejected on evidence -- there is no maintained browser stack for Python
    2.7, and the one that still installs is a 2020 Chromium that cannot render
    the engine 045 is waiting for. Option 2 was rejected because the drag
    rewrite 045 owes is exactly the change that needs a test. See "The
    decision" below for what was measured.
:Resolution: Fixed in b378bbf. The old suite and
    ``requirements/integration-tests.txt`` are gone, and with them the
    committed production password -- which turned out to be live, and is issue
    :doc:`050 <050-the-production-admin-password-is-committed-and-in-use>`.

Problem
=======

``reports/planting-labels.html`` is a 626-line Vue application -- the label editor staff
use to group, hide and photograph planting labels. The Django side is covered: the JSON
endpoint, the POST round trip, and the page's server contract (200, the ``#app`` mount
point, the data endpoint URL, the Vue script tag). **None of its actual behaviour is** --
drag and drop, the save cycle and the layout only exist in the browser.

The repository has a browser suite, ``integration_tests/``, but it cannot run:

* it hardcodes ``http://localhost:8000/`` and expects a server to be up already;
* ``conftest.py`` logs in with a real username and password committed to the repo;
* ``conftest.py`` asserts the login page URL is ``/admin/`` *before* logging in, which is
  wrong, so the fixture fails at the first assertion;
* it needs SeleniumBase and a browser, neither of which the dev container has.

Impact
======

The most complex user-facing feature in the project has no behavioural test at all, and the suite that was meant to cover it does not run.

Options
=======

1. Rebuild it on Django's ``LiveServerTestCase``, which starts its own server and needs
   no hardcoded host or committed password, and add a browser to the dev image.
2. Delete ``integration_tests/`` if it is not going to be maintained, so it stops looking
   like coverage that exists.

Related: ``dev/kasvimuseo`` would need an ``app browser-test`` entry point, and the CI
question in issue 018.

The decision
============

Nothing maintained runs in the container
----------------------------------------

The suite as written cannot be revived at all: SeleniumBase needs Python 3.7 and
the application is Python 2.7. What is left for 2.7 is ``selenium==3.141.0``,
November 2018, the last release with it -- and it is already pinned, in
``requirements/integration-tests.txt``, beside ``pytest-selenium==1.17.0``.

A browser for it does still exist, which was checked rather than assumed. The
image is ``python:2.7-alpine``, Alpine **3.11.5**, end of life since 2021; its
archived repositories still carry ``chromium`` and ``chromium-chromedriver`` at
**81.0.4044.113** (April 2020), and both install and start headless in the image
today. The cost, measured:

=========================================== =========================
 ``apk add chromium chromium-chromedriver``  +334 MB on a 334 MB image
 Time added to ``app build``                 about 11 s here
 Browser age                                 six years, unpatched
=========================================== =========================

So option 1 is possible and is still the wrong answer. It would pin the tests of
this project's most interactive page to a browser older than four of the issues
that page has, and -- the part that decides it -- Chromium cannot stand in for
the engine that matters: 045's remaining half is about **iPadOS Safari**, and a
WebKit is precisely what a 2020 Chromium is not.

The shape that was not in the options
-------------------------------------

Drive the browser from the **host**, on Python 3, against the real application
in its own container. This repository has already done that three times without
committing it: 045, 046 and 047 were each verified by rendering the page,
serving it locally with the CDN scripts replaced, and driving it in headless
Chromium and WebKit -- 046 dragged a museum number onto the background and
watched the label split, which is the interaction this issue says nothing tests.
Three ad-hoc harnesses, built and thrown away. What this fix commits is the
fourth one.

The real cost of it is that the suite is now in two halves, on two interpreters:
``kasvimuseo/tests/`` in the container on 2.7, ``browser_tests/`` on the host on
3.x. That is a genuine loss -- there is no one command that runs everything, and
a contributor has to know which is which. It is the same split ``dev/kasvimuseo
docs`` already lives with, for the same reason, and it buys the one thing the
in-container option cannot offer: Playwright drives Chromium, Firefox **and**
WebKit, so the tablet work has somewhere to go.

What it costs in CI
-------------------

A third job, ``playwright``, beside ``pytest`` and ``sphinx``. It rebuilds the
image (the jobs share no machine), installs Playwright's Chromium, and runs the
suite. Measured on the runner rather than guessed, once it had run:

======================= ======= ======================================
 Job                     Total   Of which
======================= ======= ======================================
 ``pytest``              68 s    50 s image, 13 s suite
 ``playwright``          97 s    48 s image, 24 s browser, 18 s suite
 ``sphinx``              24 s    16 s build
 **The pipeline**        97 s    the three in parallel
======================= ======= ======================================

So it costs about half a minute of wall clock, not the two and a half minutes
estimated before it ran: the browser download is 24 seconds and the image build
-- the largest item, and duplicated between two jobs -- would be the thing to
cache if this ever mattered. Locally the suite is 18 seconds plus about 10 to
build the database and start the server.

What is now tested, and what is not
===================================

Eleven tests, all of them about behaviour that only exists in a browser. The
server contract stays where it was, in ``test_views.py`` and
``test_templates.py``; nothing was moved and no Python 2.7 test was changed.

============================================ ================================
 Behaviour                                    Why it is worth pinning
============================================ ================================
 A museum number dragged onto the background  The editor's reason to exist,
 splits its label in two                      and what 045 rewrites
 A number dragged onto another label of the   The other half of it; the
 same species merges, and the emptied label   emptied label must not print
 disappears                                   blank
 Save posts the whole sheet, and the reload   ``post`` deletes and recreates
 agrees with it                               every label (010, 039)
 The chevrons change **that** label's photo   039's fix, and the sentence 037
 and no other, and it survives a reload       added above the sheet
 A label with one photo gets no chevrons      They would walk in a circle
 Clicking the printer flips the checkbox      047's fix; the ``<label for>``
 and takes the label out of the print run     it replaced could not
 Save is disabled until something changes     Saving nothing would delete
                                              every label
 A truncated data response leaves the editor  044: a partial list in this
 empty, and says so                           editor is a destructive save
 A species planted only in a private bed      The public-visibility rule, end
 gets no label                                to end
============================================ ================================

**Not covered, and named so it is not mistaken for covered:** the print
rendering (what lands on A4 is checked by printing to PDF, by hand, as 046 and
047 did), anything on a real device, and the touch path -- Playwright's WebKit
is an engine, not an iPad. The suite runs Chromium only; adding Firefox and
WebKit is a line in the ``browser`` fixture and was left for whoever needs them.

What this changes for the issues 017 names
==========================================

Their ``Status`` fields are untouched. This is what each can now assume.

``045`` -- **the large half may proceed.** Its own file says the pointer-events
rewrite "wants issue 017 first", because it rewrites the one part of the editor
with no coverage. That part now has coverage: the two drag tests fail if a
number can no longer be moved between labels with a mouse, which is the
regression the rewrite risks. What the suite still cannot do is prove the new
path works *by touch* -- Playwright can emulate a touch context, and that is
worth writing, but the device itself stays the reporter's job.

``046`` -- its zoom is now indirectly asserted, not directly. The tests drive
the page at 50 % and the drag arithmetic depends on it, so a change to
``--screen-scale`` that broke the drag preview would be caught; the measurements
in 046's own resolution (labels per row, printed centimetres) are not repeated
here, because the printed size is the half a browser cannot see.

``047`` -- covered. The printer icon is now clicked by a test, and the checkbox
it flips is asserted. Its ``:Evidence:`` says "(none -- the suite asserts the
page's server contract, not its glyphs)"; that is still true of the glyph, which
is a shape on a screen, and no longer true of the control.

``039`` and ``010`` -- covered from the other end. Both were fixed with
server-side tests that POST and GET directly; the browser now performs the same
round trip through the actual buttons, so the JSON contract between the editor
and the API is asserted by something that speaks both sides.

``013`` -- **not settled, and this does not settle it.** Its option 2 wants a
browser test of the admin's filtering and its changelist action. The suite this
issue builds is about the label editor; it is now cheap to add an admin test to
it, which is a decision for 013 rather than a change to make here.

What the suite found on its first run
=====================================

Both are in ``docs/issues/incoming.rst`` rather than given numbers here, which
is where new reports go.

* **A save from a page nobody reached through the admin does nothing at all**,
  silently. ``save`` reads the ``csrftoken`` cookie with ``match(...)[1]``, and
  the editor sets no such cookie -- it renders no ``{% csrf_token %}``, so
  ``CsrfViewMiddleware`` never issues one. Staff arrive from the admin, which
  does, so it has never been noticed. Pinned by
  ``test_saving_without_an_admin_cookie_does_nothing_and_says_nothing``, which
  asserts today's behaviour and must be changed by whoever fixes it.
* **The museum numbers on a label arrive in an arbitrary order.**
  ``get_labels_data`` calls ``sorted()`` on ``Observation`` instances, which
  define no ordering, so Python 2 compares them by identity. The editor's own
  ``insort`` sorts numerically, so the same label prints "12 11" until somebody
  drags a number and "11 12" afterwards.

It has run on a runner
======================

The ``playwright`` job passed on a hosted runner at the first attempt, on
`pull request 2 <https://github.com/akaihola/kasvimuseo/pull/2>`_: eleven tests
in 12.5 s, the whole ``app browser-test`` step 18 s on top of the image build
and the browser download. So the two assumptions this shape rests on are facts
rather than expectations -- rootless podman does run this server with
``--network=host`` on ``ubuntu-latest``, and a browser installed by
``playwright install`` is found by the ephemeral environment ``uv`` builds for
the suite.

The same run found the one thing this fix had left rough, and found it the way
a new entry point usually is found -- by somebody typing it on a second machine.
``dev/kasvimuseo app browser-test`` on a checkout whose development image had
never been built failed with podman's::

    Error: ... requested access to the resource is denied

because an image podman cannot find locally is a Docker Hub short name to it, so
it tried to pull ``docker.io/library/kasvimuseo-dev``. That reads as a
credentials problem and is not one. ``app_run_container`` now checks
``podman image exists`` first and says to run ``app build``; it is not specific
to the browser tests -- every ``app`` subcommand had the same first-run
failure -- but this is the command that met it.

How to run it
=============

::

    $ dev/kasvimuseo app browser-test          # everything
    $ dev/kasvimuseo app browser-test -k drag  # or any pytest arguments

It builds its own database, ``ylaneenkasvit_browsertest``, from
``browser_tests/seed.py``, serves it with gunicorn on a free port, runs the
tests, and drops the database again. The developer's own database, ``media/``
and ``local_settings.py`` are not touched: the server runs on
``ylaneenkasvit.test_settings``, whose ``MEDIA_ROOT`` this command points at
``.dev/browser-test-media``.

Two things are faked in the browser and nothing else. The page loads Vue, axios
and sanitize.css from ``unpkg.com`` and ``cdnjs.cloudflare.com``; the tests
answer both from ``browser_tests/vendor/``, so a run needs no network and cannot
go red because a CDN did. That is also the only place this repository pins what
the page actually loads: Vue is pinned in the template at 2.6.14, axios is not
-- ``unpkg.com/axios`` is whatever is current -- so production floats where the
tests are fixed. And the truncated response of 044, which cannot be asked of the
real server, is served by the test.

The browsers themselves are never downloaded by the script. CI runs
``playwright install --with-deps chromium``; a development machine sets
``PLAYWRIGHT_BROWSERS_PATH`` at the copy it already has.
