Incoming issues to be split into individual files
=================================================

Write new reports here in whatever shape they arrive -- a sentence is enough --
and they get split into numbered files under ``docs/issues/`` with the causes
traced as far as they go.

Waiting
-------

* **The museum number is not visible while it is being dragged on the iPad.**
  Reported on 2026-08-02, from the tablet, while checking :doc:`056
  <056-ipad-label-text-is-doubled-and-grows-until-it-vanishes>`'s first half --
  which is why it is here rather than in that file: it is the drag layer of
  :doc:`045 <045-the-label-editor-is-unusable-on-an-ipad>` rather than the
  fitter, and one report per file is the rule.

  Nothing is traced yet. What to look at first: ``#drag-number`` is the copy
  that follows the pointer, it sits outside ``#labels`` so 046's ``zoom`` does
  not apply to it, and ``dragStart`` gives it an inline ``font-size`` computed
  as the number's ``getBoundingClientRect().width / offsetWidth`` times its
  computed ``font-size``. Those are the two coordinate systems 746ce71 says
  Safari reports differently inside a zoomed subtree, so a size of zero or of
  something absurd is the first thing to measure. 045's own emulated touch
  tests cover the drag itself and pass, so whatever this is, it is not the
  gesture.

  It is not known whether the number still moves and is merely invisible, or
  whether the gesture does nothing at all. The report says only that the number
  is not visible, so ask before assuming either.

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

Emptied of the last report it arrived with, on 2026-08-01: the iPad label text
became :doc:`056 <056-ipad-label-text-is-doubled-and-grows-until-it-vanishes>`.
That took this page to nothing waiting for the first time since it was written,
and it stayed there for part of a day: the production image with no templates
of its own, above, arrived from the upgrade plan's Stage 1 the same evening. It
is the one report here that was overtaken while it waited: a commit landed on
``master`` that says it fixes exactly this, so splitting it out was a
verification before it was a filing, and the two halves came apart under it.
The first -- a label whose photo never loads is never fitted -- is fixed and
now has three browser tests that go red against the template as it was, which
is the thing the commit message alone could not establish. The second, the text
that grows until it vanishes, is where it was: never reproduced off the device,
and now covered by a change that runs behind an ``@supports`` test neither of
this host's Playwright engines implements, so nothing here can watch it work.
That is why 056 is ``Accepted`` rather than ``Fixed`` and why its "What is
left" is a list of things to look at rather than to write. The question the
report parked -- why the photos fail at all -- went the same way: the page's
URLs and :doc:`048 <048-the-dev-server-loads-photos-from-the-production-media-host>`
narrow it to two things about the machine the development server runs on, and
neither is a defect anybody here can show, so it is recorded in 056 rather than
given a number of its own. It also stopped being the more urgent half: a label
is fitted now whether its photo arrives or not.

The next day the tablet answered, which is the one thing none of the above
could do: the text is the right size and the names fit, so 056's first half is
confirmed where it was reported. The same look put the second of the two
reports above on this page -- the museum number that cannot be seen while it is
dragged -- and left 056's photo question exactly where it was, since the photos
are still not all there. A report that has been to the device once is cheaper
to settle than one that has not, and both of these have now.

Emptied of the templateless production image on 2026-08-02: it became
:doc:`058 <058-the-production-image-ships-none-of-the-projects-own-data-files>`,
and it is fixed. The report guessed its own cause and named it unverified, and
the guess was right down to the line -- ``COPY MANIFEST.in`` -- so what the
split was actually for was the two things a guess cannot do. The first is that
the fault is bigger than the report: the manifest carries ``*/locale`` as well
as ``ylaneenkasvit/templates``, so the image was missing both of this project's
own Finnish catalogs too, and the admin the running image showed spoke English
in exactly the strings :doc:`040
<040-django-ships-no-translations-so-the-admin-chrome-is-english>` was written
about. Nobody had looked, because nobody renders a page in order to read its
headings. The second is the question the report parked, and it was answered by
reading rather than by asking: ``ansible/install.yaml`` installs production
with ``pip`` from a git URL and ``.github/workflows/tests.yml`` builds the
development image twice and this one never, so no deployment and no pipeline
has ever built this file. That makes the defect one with no user -- which is
its rank and its ``Medium``, and not a reason to leave it, since an image
nobody deploys is exactly what somebody with no development checkout reaches
for. The fix carries the assertion that makes the next reorganised ``COPY``
fail the build instead of the gallery page. That leaves the iPad drag number as
the only report here.
