Incoming issues to be split into individual files
=================================================

Write new reports here in whatever shape they arrive -- a sentence is enough --
and they get split into numbered files under ``docs/issues/`` with the causes
traced as far as they go.

Waiting
-------

* **Label text is about twice the size it should be, and on the labels whose
  photo loads it grows until it disappears.** Reported from the iPad on
  2026-07-31, while looking at :doc:`045
  <045-the-label-editor-is-unusable-on-an-ipad>`'s cheap half. Two symptoms,
  split by whether the photo arrives. On the majority, where it does not, the
  text is simply too big and stays that way. On the seven top labels where it
  does, the text starts at that same doubled size, grows every few seconds, and
  eventually vanishes.

  The first half has a cause in the template, and it is one line of control
  flow: ``reports/planting-labels.html`` fits text to the label with fitty, and
  the only thing that ever calls ``fitTextToSpace`` is the ``verticalPhotoWidth``
  watcher. That property changes in ``setAspect``, which runs on the photo's
  ``@load``. **No photo, no fit** -- the text keeps the declared ``30pt`` /
  ``24pt``, which on a label drawn at 046's 50 % is about double what a fitted
  label shows. Reproduced in emulated WebKit and Chromium: with half the labels'
  photos 404ing, every one of them reports ``font-size: 40px`` and never changes.

  The second half is **not reproduced here**. In the same emulation the fitted
  labels are stable across repeated fit passes, and nothing grows. One suspect
  was tested and cleared: fitty measuring inside 046's ``zoom: 0.5`` returns the
  same font size as without it (22.69px vs 22.67px in WebKit, 24.23 vs 24.18 in
  Chromium, unchanged over three passes), so the zoom is not corrupting its
  arithmetic -- do not re-test that. What is left to suspect is iOS text
  autosizing (``-webkit-text-size-adjust``, which the page gets only from the
  CDN copy of sanitize.css) and fitty's own resize observers on the device.
  Settling it wants the device, or :doc:`017
  <017-browser-suite-unrunnable-vue-editor-untested>`'s browser suite, which is
  also the argument for not fixing it blind.

  Worth asking before it is split: **why do the photos fail at all?** The report
  says the majority do not load, and that is the trigger for the first half. If
  the tablet cannot reach the media host, that is a serving question in the
  neighbourhood of :doc:`048
  <048-the-dev-server-loads-photos-from-the-production-media-host>` rather than
  a template one, and it would be the more useful thing to fix first.

  It's good to have iPad Safari debug capability before tackling this issue.
  See ~/repos/nixos-config/ and Kandev task d7054db3-97e1-4650-98d7-11232e22c502.

* **``initial_data.json`` is never installed on a database built the way**
  ``db bootstrap`` **builds one, so such a database has no photo sizes at
  all.** Found on 2026-08-01 while checking :doc:`054
  <054-the-species-list-names-a-photo-size-the-fixtures-lack>` in the running
  application. ``syncdb`` loads the project fixture before South has created
  photologue's tables and dies on the first row::

      DatabaseError: Problem installing fixture
      '/src/ylaneenkasvit/fixtures/initial_data.json': Could not load
      photologue.PhotoSize(pk=1): relation "photologue_photosize" does not exist

  Nothing loads it afterwards: South's own "Loading initial data" pass is per
  application, and ``ylaneenkasvit`` has no migrations for it to run under.
  ``dev/kasvimuseo``'s comment calls this "noise rather than a failure" and
  says photologue's own initial data supplies ``display``; both halves are
  wrong -- the fixture is not installed, and ``migrate photologue`` reports
  ``Installed 0 object(s) from 0 fixture(s)``. On a freshly bootstrapped
  database ``SELECT * FROM photologue_photosize`` returns only the row 054's
  data migration writes, so ``display`` and ``admin_thumbnail`` are missing too
  and every photo on every report and in the admin changelist renders
  ``src=""``. The test database is unaffected, because
  ``SOUTH_TESTS_MIGRATE = False`` makes ``syncdb`` create every table at once
  and the fixture then loads cleanly -- which is why the suite has never seen
  it. What it wants before it is worth a number is a decision about where the
  three photologue rows belong: a data migration like 054's, a fixture loaded
  after ``migrate`` rather than during ``syncdb``, or a documented
  ``loaddata`` step in ``db bootstrap``.

Last emptied on 2026-07-29: the five reports that were here became issues
:doc:`043 <043-photos-cannot-be-sorted-by-file-name>`,
:doc:`044 <044-large-admin-pages-are-truncated-for-a-remote-browser>`,
:doc:`045 <045-the-label-editor-is-unusable-on-an-ipad>`,
:doc:`046 <046-the-label-editor-opens-at-print-size>` and
:doc:`047 <047-the-label-print-toggle-glyph-has-no-font-on-linux>`. The
follow-up questions those raised were answered the same day, and the answers
settled all five: 044 turned out to be a truncated response rather than an
admin defect and is being worked as its own task, 045 has its scope, 046 and
047 have their rulings, and 043 was asked for as work from the start. None is
waiting on a decision.

Emptied again on 2026-07-30: one report arrived, a ``JSON.parse`` error from
``/kasvimuseo/planting-labels/data/``, and it got no number of its own. It is
the same truncated response as
:doc:`044 <044-large-admin-pages-are-truncated-for-a-remote-browser>` on a
second URL -- one that carries no admin, no login and no HTML -- so it was
filed there as evidence instead. It narrows that issue's three suspects to two
and gives it a one-command reproduction.

Emptied again on 2026-08-01: the silent save became :doc:`052
<052-saving-the-label-editor-does-nothing-without-an-admin-cookie>`, and it is
fixed. The maintainer ruled on all three of the questions in it, and the third
one is the reason this entry is longer than the report was: settling it meant
establishing what protected that endpoint, and the answer was nothing at all,
so the same pull request closed it. The page renders the token and issues its
own cookie, a save that finds none says so, and both the editor and its data
endpoint are staff-only -- which is also why the browser suite now logs in.
The other three reports here are untouched.

Emptied of one more on 2026-08-01: the museum numbers arriving in an arbitrary
order became :doc:`053
<053-museum-numbers-on-a-label-are-in-an-arbitrary-order>`, and it is fixed.
The question that kept it here -- where an observation with no ``external_id``
belongs in that order -- was put to the maintainer with the data behind it and
ruled the same day: numerically, with a missing number first. The data is why
that answer was cheap. The production dump has no such row, and the two other
places that sort the same list both put a missing number first, so the ruling
changes nothing anybody can see today and only says what happens when the
nullable column is finally used. The two reports left on this page -- 052
removed one the same day -- are untouched.

Emptied of one more the same day: the missing ``mobilethumbnail`` photo size
became :doc:`054
<054-the-species-list-names-a-photo-size-the-fixtures-lack>`, and it is fixed
too. The question that had kept it here -- whether production has the row --
was answered without asking anybody, by the ``photologue_photosize`` block of
the dump in ``.dev/backups/``, which has it. That halved the issue: a fixture
gap and not a live defect. That leaves the iPad label text as the one report
this page arrived with; checking 054 in the running application added the
second one, which is new rather than left over.
