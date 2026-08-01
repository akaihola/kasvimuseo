Incoming issues to be split into individual files
=================================================

Write new reports here in whatever shape they arrive -- a sentence is enough --
and they get split into numbered files under ``docs/issues/`` with the causes
traced as far as they go.

Waiting
-------

* **The production image ships no** ``ylaneenkasvit/templates/``, **so every
  page that extends** ``base.html`` **is a 500 in it.** Found on 2026-08-01
  while verifying Stage 1 of the upgrade plan, which is how a page got
  rendered from the production ``Dockerfile`` image at all. ``/admin/``,
  ``/accounts/login/`` and ``/kasvimuseo/planted-species/`` answer 200;
  ``/photologue/gallery/`` answers 500, and with ``DEBUG`` forced on it is
  ``TemplateDoesNotExist: base.html``.

  Not caused by that stage, and not by the ``django-extensions`` change beside
  it: the same directory is missing from ``kasvi-027-prod``, an image built
  from this repository before either. The cause is one missing line rather
  than anything subtle. ``setup.py`` names ``kasvimuseo`` and ``jqm``
  templates in ``package_data`` explicitly, and those are in the image;
  ``ylaneenkasvit/templates/*.html`` -- ``base.html``, ``404.html``,
  ``500.html`` and ``grappelli/`` -- comes only from ``MANIFEST.in`` plus
  ``include_package_data``, and ``Dockerfile`` never copies ``MANIFEST.in``
  into the build context it installs from. ``COPY MANIFEST.in`` is the
  suspected whole of it, unverified.

  Worth settling before it is split: **is this image deployed anywhere?**
  Production is installed by ``ansible/install.yaml`` from a checkout, not
  from a container, and nothing in this repository builds or pushes this
  image, so the fault may have no user. That answer decides whether this is a
  defect or a definition of a thing nobody runs -- and either way the image is
  what a reader would reach for to see the application without a development
  checkout.

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

Emptied of that second one on 2026-08-01, the day after it arrived: the
fixture that never reaches a bootstrapped database became :doc:`055
<055-initial-data-never-reaches-a-bootstrapped-database>`, and it is fixed.
This is the one report on this page whose open question was not a question
about the world -- nothing had to be found out from a machine, a browser or a
person, because everything it needed was in the tree. What it wanted was a
choice between three repairs, and the difference between them was an argument
rather than a fact: the maintainer was given all three with the evidence and
took the second, a fixture loaded after ``migrate``, which turned out to be
one ``git mv`` because ``kasvimuseo`` has migrations and ``ylaneenkasvit``
never did. It also repairs the databases that are already wrong, which the
other two would not have, so nobody has to be told to rebuild anything. The
iPad label text is once again the only report here, and it is still waiting on
the device or on :doc:`017 <017-browser-suite-unrunnable-vue-editor-untested>`.
