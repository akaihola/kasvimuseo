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


* **The species list page names a photo size that is not in the initial data.**
  ``reports/planted-species-list.html`` renders
  ``species.photo.get_mobilethumbnail_url``, but
  ``ylaneenkasvit/fixtures/initial_data.json`` defines only
  ``admin_thumbnail``, ``thumbnail`` and ``display``. Photologue attaches
  ``get_<size>_url`` only for sizes that are in the database, so where that row
  is missing the accessor does not exist, the template renders ``src=""``, and
  the list shows a broken image for every species. Found while covering
  :doc:`011 <011-species-report-opens-every-image-file-to-pick-a-css-class>`,
  whose test had to create the size to have a photo to assert about. Whether
  production is affected is exactly the open question: ``initial_data.json`` is
  loaded at ``syncdb``, so a ``mobilethumbnail`` row added by hand years ago
  would be in the production database and in no dump this repository has. It
  needs one ``SELECT name FROM photologue_photosize`` on the server before it
  is worth a number -- if the row is there, the fix is a line of fixture so a
  fresh database matches; if it is not, it is also a visible defect in
  production.

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
