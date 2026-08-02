==================
Test coverage plan
==================

A plan for growing the automated test suite of the Kasvimuseo app, written
against Django 1.5 on Python 2.7 and the ``dev/kasvimuseo`` development
environment from the ``dev-environment`` branch.

Every claim about tooling below was verified by running it in the
``kasvimuseo-dev`` container; the two defects in `Defects already found`_ were
found by writing the probe tests this plan proposes.


Baseline
========

Measured with::

    $ podman run --rm -v "$PWD:/src" -w /src/kasvimuseo kasvimuseo-dev sh -c \
        "pip install -q coverage==4.5.4;
         coverage run --source=/src/kasvimuseo --omit='*/migrations/*,*/tests/*' \
                      -m pytest tests -q;
         coverage report -m"

===================================== ======= ====== =======
Module                                  Stmts   Miss   Cover
===================================== ======= ====== =======
admin.py                                  122    122      0%
forms.py                                   21     21      0%
models.py                                 289     91     69%
photos.py                                  19      0    100%
templatetags/bush.py                        5      5      0%
templatetags/kasvimuseo_admin_list.py     139    139      0%
templatetags/kasvimuseo_model_tags.py       6      6      0%
templatetags/kasvimuseo_photo_tags.py       7      7      0%
templatetags/lightings.py                   7      7      0%
templatetags/months.py                      7      7      0%
urls.py                                     3      3      0%
views.py                                  100    100      0%
**TOTAL**                                 727    510     30%
===================================== ======= ====== =======

The 30 % is flattering and the 69 % for ``models.py`` especially so: nearly all
of it is model field declarations executed at import time. Outside
``photos.py``, **no application behaviour is covered at all** -- not one model
method, view, form, admin callable or template tag.

There are two existing suites:

``kasvimuseo/tests/test_photos.py``
    8 tests, pure ``mock``, no database. Fast and green, but they mock
    ``photologue.models.Photo`` entirely, so they cannot catch a change in the
    photologue API -- only a regression in our own grouping logic.

``integration_tests/`` -- **deleted since**
    SeleniumBase browser tests. They hardcoded ``http://localhost:8000/`` and a
    real username/password, and ``conftest.py`` asserted the login page URL was
    ``/admin/`` before logging in. Effectively unrunnable, which is why this
    plan excluded them; see `Out of scope`_. Issue 017 replaced them with
    ``browser_tests/``, on the host's Python 3, and the password turned out to
    be production's (issue 050).


What the Django 1.5 testing docs give us
========================================

From ``topics/testing/overview`` and ``topics/testing/advanced``:

* **Test discovery.** Django 1.5's own runner only finds tests in each app's
  ``models.py`` or ``tests.py``. A ``tests/`` *package* like ours is invisible
  to it. This project already uses ``pytest`` + ``pytest-django`` 2.9.1
  instead, which is why ``kasvimuseo/tests/`` works. **Keep pytest**; do not
  migrate to ``manage.py test``.

* **Case classes.** ``SimpleTestCase`` for anything that needs no database
  (template tags, forms, ``photos.py``); ``TestCase`` for the rest -- it wraps
  each test in a transaction and rolls back, which is much faster than
  ``TransactionTestCase``'s table truncation. Under pytest-django these map to
  plain functions and ``@pytest.mark.django_db``.

* **Test client** (``self.client`` / pytest-django's ``client`` and
  ``admin_client`` fixtures) exercises the full request path including URLconf,
  middleware and template rendering, without a running server. This is what
  makes the report views cheap to cover.

* **RequestFactory** runs *no middleware* -- ``request.user`` and session must
  be set by hand. Use it only for the view methods that take a request but do
  not need auth (``PlantedSpecies.get`` and its ``HTTP_REFERER`` branch).

* **Assertions worth using here**: ``assertContains``, ``assertRedirects``,
  ``assertQuerysetEqual``, ``assertNumQueries`` (the ``public_planted()``
  managers are documented as "NB! This evaluates the queryset!" -- pin their
  query counts), ``assertHTMLEqual``.

* ``override_settings`` / the ``settings`` fixture for ``MEDIA_ROOT`` and
  ``MEDIA_URL`` in the printable-report tests.

* **1.5 ordering caveat.** In 1.5 the run order of unittest subclasses changed
  and is no longer guaranteed. Write every test self-sufficient; never lean on
  data left behind by another test.


The blocker, and its fix
========================

A test database cannot currently be built at all. South migrates apps in
alphabetical order, so ``kasvimuseo`` runs before ``photologue``, and
``kasvimuseo/migrations/0014`` adds a foreign key to ``photologue_photo``::

    DatabaseError: relation "photologue_photo" does not exist

This is the same ordering problem ``dev/kasvimuseo db bootstrap`` works around
by hand (``migrate photologue`` first, then everything else).

**Fix**: set ``SOUTH_TESTS_MIGRATE = False`` in the test settings. South then
leaves test-database creation to ``syncdb``, which builds every table straight
from the models and has no ordering problem. Verified: with that one setting,
model, manager, template-rendering view and JSON API tests all pass against the
local cluster.

This is also the *right* choice on its own merits -- the migration history is a
2013-era South chain we do not want to replay on every test run.


Infrastructure to put in place first
====================================

1. ``ylaneenkasvit/test_settings.py`` -- imports ``ylaneenkasvit_settings``,
   then::

       SOUTH_TESTS_MIGRATE = False
       PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)
       MEDIA_ROOT = <a temporary directory>
       LOGGING['loggers']['django.request']['handlers'] = []

   The existing ``kasvimuseo/test_settings.py`` (three lines, ``SECRET_KEY``
   only) stays for the database-free tests, or is folded in once one settings
   module can serve both.

2. **One pytest invocation for both suites.** Move ``pytest.ini`` to the repo
   root with ``DJANGO_SETTINGS_MODULE = ylaneenkasvit.test_settings`` and
   ``testpaths = kasvimuseo/tests``, so the mock tests and the database tests
   run together.

3. ``kasvimuseo/tests/factories.py`` -- plain helper functions (not
   ``factory_boy``; it would have to be pinned for 2.7) that build the
   Plot/Bed/Location/Species/Observation/Planting/Care graph the whole suite
   needs, with keyword knobs for ``public``, ``removed`` and care history. The
   visibility rules are the thing under test, so the builders must make each of
   those states easy to construct.

4. ``dev/kasvimuseo app test`` currently runs the container **without** the
   database, on the comment "The unit tests are pure mocks, so they need no
   database." That stops being true with P1. Route it through ``with_db`` and
   mount the socket, exactly as ``app manage`` does.

5. **Coverage.** ``pytest-cov`` cannot be used: 2.8.1 requires ``pytest>=3.6``
   while pytest-django 2.9.1 needs the pinned ``pytest==3.5.0``. Use
   ``coverage run -m pytest`` instead -- verified working. Add
   ``coverage==4.5.4`` to ``dev/Containerfile`` and a
   ``dev/kasvimuseo app coverage`` subcommand.

6. ``requirements/testing.txt`` is stale -- it lists ``nose``, ``nose-django``
   and ``mock``, none of which reflect how tests actually run. Align it with
   the image: ``pytest==3.5.0``, ``pytest-django==2.9.1``, ``mock==2.0.0``,
   ``coverage==4.5.4``.


Work packages
=============

Ordered by risk × cost, each independently mergeable.

P1 -- Public-visibility logic (``models.py``)
---------------------------------------------

The highest-value target in the codebase: these methods alone decide what the
public site shows, they are subtle, and they are entirely untested.

* ``SpeciesManager.public_planted``, ``ObservationManager.public_planted``,
  ``PlantingManager.public_planted``, ``Planting.is_public_planted``
* Cover the full matrix: private bed; ``removal_date`` set; no care records at
  all; last care ``count == 0``; last care ``count > 0``; several care records
  entered out of date order (``last_care`` sorts by date, not by pk).
* ``Planting.last_care`` has **two code paths** -- the ``_prefetched_objects_cache``
  branch and the plain query -- and only the prefetch branch is used by the
  managers. Test both, and assert they agree.
* ``last_care_date`` / ``last_care_description`` / ``last_care_count``
  fall back to ``u''`` via ``except AttributeError``; note that
  ``is_public_planted`` compares that ``u''`` against ``0``.
* ``__unicode__`` of ``Species``, ``Observation`` (variation branch), ``Bed``
  (plot branch), ``Label`` (photo and hidden branches), ``Care``.
* ``Species.flowering_time`` -- ``None`` start, start only, start and end.
* ``assertNumQueries`` around each ``public_planted()`` to pin the cost of the
  documented "NB! This evaluates the queryset!" behaviour.

Roughly 15 tests. Target: 100 % of the non-declarative lines of ``models.py``.

P2 -- Views and the labels API (``views.py``, 0 %)
--------------------------------------------------

* ``PlantedSpeciesList`` -- only public planted species, ordered by
  ``name_fi``, deduplicated.
* ``PlantedSpeciesLabelsApi.get`` -- JSON shape, grouping by species, species
  that have a ``Label`` versus species that do not, the ``visible`` flag.
* ``PlantedSpeciesLabelsApi.post`` -- the riskiest code in the app. It deletes
  **all** labels, bulk-creates replacements, then re-links plantings by
  ``zip(items, labels)``, i.e. it assumes ``bulk_create`` hands back rows in
  input order. A single-item round-trip already passes; the tests that matter
  use several items with non-sequential primary keys, and assert that a failure
  partway does not leave the labels table empty.
* ``PlantedSpecies.get_context_data`` -- ``previous``/``next`` adjacency at
  both ends of the alphabet, beds filtered to ``public=True``, ``origins``
  deduplication, ``local_names`` skipping empty nicknames.
* ``PlantedSpecies.get`` -- the ``HTTP_REFERER`` branch. Note that it sets a
  top-level ``context['next']`` to a URL while the templates only read
  ``pages.0.next``, a ``Species``. Pin the current behaviour in a test, then
  decide whether the branch is dead.
* ``planted_observation`` -- 404 for an unknown external id; the ``texts`` list
  assembled from ``history`` and ``stories``.
* ``BedMap`` -- ``bed_depth=40`` reaches the context.
* ``PlantedSpeciesPrintable`` / ``PlantedSpeciesCompact`` -- these render
  templates that make Django open the image files to read their dimensions, so
  they raise ``IOError`` when media is missing (the README warns about exactly
  this). Generate a 1×1 JPEG into a temporary ``MEDIA_ROOT`` rather than
  depending on ``dev/kasvimuseo media fetch``.

Roughly 15 tests. This package also gives the report templates their first
coverage of any kind.

P3 -- Cheap pure-function wins (template tags, ``forms.py``)
------------------------------------------------------------

No database, fast, and takes six modules from 0 % to ~100 %.

* ``months.month_name`` and ``lightings.lighting_name`` -- valid number, and
  the falsy ``0``/``None`` branch.
* ``bush.bush_shadow`` -- width < depth, width > depth, equal.
* ``kasvimuseo_model_tags.nicknames`` (excludes empty) and ``external_ids``
  (sorted).
* ``kasvimuseo_photo_tags.get_photo_orientation`` -- both sides of the
  ``3.1/4.0`` threshold, and exactly on it.
* ``forms.PhotoForm.clean`` -- title derived from the filename, extension
  stripping for ``jpg``/``jpeg``/``jpe`` and their uppercase forms, slug with
  diacritics removed, and the branch where a title was supplied. This also
  guards a Python 3 migration hazard: ``remove_diacritics`` uses ``filter()``,
  which returns an iterator rather than a string on Python 3.

Roughly 10 tests.

P4 -- Admin (``admin.py``, 0 %)
--------------------------------

* Display callables, called directly -- ``PlantingAdmin.coordinates``,
  ``BedAdmin.map``, ``PhotoAdmin.image_filename``, ``SpeciesAdmin.photo_image``
  (including the ``photo is None`` branch).
* The ``planted_species_report`` action -- redirects to ``planted-species``
  with comma-joined external ids; and what it does when an id is ``NULL``.
* **Smoke tests with the ``admin_client`` fixture**: the changelist and the add
  page of every registered model return 200. Eight models, one parametrised
  test, and it is what catches import-time and form-construction breakage --
  including the empty-database crash in `Defects already found`_.

P5 -- Signals and integration edges
------------------------------------

* ``autoconnect_photo_to_species`` -- a ``post_save`` receiver connected at
  import for *every* model. Test: matches on the lowercased first word of the
  title; only fires when the species has no photo yet; ignores non-``Photo``
  senders; tolerates an empty title.
* ``photos.py`` -- add one database-backed test next to the existing mocks, so
  a photologue API change is caught. The mocks cannot see one.


Defects already found
=====================

Found while validating this plan. Each should be fixed *with* the regression
test that exposes it.

1. **``models.py:178`` -- ``Species.nicknames()`` is broken.** It calls
   ``self.observation_set.planted_public()``; ``ObservationManager`` defines
   ``public_planted()``. Raises ``AttributeError``. It has no callers, so it is
   dead code -- delete it, or fix and use it.

2. **``get_next_observation_extid()`` crashes on an empty database.** It does
   ``[0]`` on an unfiltered queryset, so with no ``Observation`` rows it raises
   ``IndexError``. It is the lazily evaluated ``help_text`` of
   ``Observation.external_id``, so **the admin's Observation add and change
   forms raise on a fresh database** -- precisely the state
   ``dev/kasvimuseo db bootstrap`` leaves a new developer in. The P4 admin
   smoke tests catch this.

3. **``PlantingAdmin.coordinates`` never shows width and depth.** The format
   string reuses ``{0}`` and ``{1}``::

       u'({0}cm,{1}cm)<br>{0}×{1}cm'.format(
           obj.distance_left, obj.distance_front, obj.width, obj.depth)

   so the second pair repeats the offsets and ``width``/``depth`` are dropped.

4. **``views.get_labels_data`` prints to stdout on every request** (two
   ``print`` statements, one per species added). Noise in production logs;
   remove or convert to ``logging``.


Out of scope
============

``kasvimuseo/templatetags/kasvimuseo_admin_list.py`` (139 statements, the
single largest uncovered module) is a vendored fork of Django's own
``admin_list`` carrying the patch from Django ticket #11195. Unit-testing a
vendored fork of framework code is poor value; it gets covered incidentally by
the P4 admin changelist smoke tests, and should be **excluded from the coverage
target** rather than chased.

Also excluded: ``kasvimuseo/migrations/`` (South history, replaced by
``syncdb`` in tests), and the browser suite, which was its own piece of work and
has since been done -- not as the ``LiveServerTestCase`` this sentence assumed,
because no browser stack supports Python 2.7 any more, but as ``browser_tests/``
on the host. It is measured by nothing here: this plan's coverage numbers are
``coverage run -m pytest`` inside the container, and that suite runs outside it.


Targets and definition of done
==============================

* After P1 + P2: ≥ 70 % on ``models.py`` and ``views.py`` together, and every
  public-visibility branch covered.
* After P3 + P4: ≥ 80 % overall, excluding ``kasvimuseo_admin_list.py`` and
  ``migrations/``.
* ``dev/kasvimuseo app test`` is green, completes in under a minute, and needs
  **no production dump and no media download** -- every test builds its own
  data.
* ``dev/kasvimuseo app coverage`` prints the table above with the new numbers.

There is no CI yet, so the gate is the dev script, not a build server. Adding
CI is a natural follow-up once the suite needs a database.


Outcome
=======

All five packages are implemented. 150 tests, green in 8 seconds, no
production dump and no media download. Coverage went from 30 % to **97 %**:

===================================== ======= ====== =======
Module                                  Stmts   Miss   Cover
===================================== ======= ====== =======
admin.py                                  122      0    100%
forms.py                                   21      0    100%
models.py                                 288      3     99%
photos.py                                  19      0    100%
templatetags/bush.py                        5      0    100%
templatetags/kasvimuseo_admin_list.py     139     19     86%
templatetags/kasvimuseo_model_tags.py       6      0    100%
templatetags/kasvimuseo_photo_tags.py       7      0    100%
templatetags/lightings.py                   7      0    100%
templatetags/months.py                      7      0    100%
urls.py                                     3      0    100%
views.py                                   98      0    100%
**TOTAL**                                 722     22     97%
===================================== ======= ====== =======

``kasvimuseo_admin_list.py`` reached 86 % incidentally through the admin
changelist smoke tests, without being tested directly -- as intended.

Defects 1--4 are fixed. Three further findings came out of writing the tests
and are **not** fixed, because each changes behaviour that is visible in
production and so wants a decision first: the public species list showing
removed species (``docs/issues/001``), the Create Species Sheets action
raising on a species with no external id (``docs/issues/009``), and the photo
auto-attach receiver being able to break every Photo save
(``docs/issues/002``, with the matching semantics in ``docs/issues/003``).

Two notes for whoever writes the next tests:

* ``django.utils.translation.override('en')`` raises in this install -- there
  is no English catalog on disk. Use ``override(None)`` to deactivate
  translations instead.
* ``PlantedSpecies.get``'s ``HTTP_REFERER`` branch is **not** dead, contrary to
  the guess in P2 above: ``planted-species-base-printable.html`` renders the
  top-level ``{{ next }}`` as its only "Jatka >>" link.


Second round: user-facing functionality
=======================================

97 % line coverage turned out to overstate how much *functionality* was
verified. Four gaps were left:

* **No admin form had ever been submitted.** All 25 admin tests were GETs or
  direct method calls, so inlines, validation and saving were untested, and
  ``forms.py`` reached 100 % through unit tests of ``PhotoForm.clean`` alone.
* **The project package was not measured at all** -- ``--source=kasvimuseo``
  hid ``ylaneenkasvit/dashboard.py`` at 0 %.
* **The customised admin changelist output was never asserted**, though
  emitting field-name CSS classes is the only reason the vendored
  ``kasvimuseo_admin_list`` fork exists.
* **The report templates were checked only to "200, and the name appears"**.

Four more packages close those: ``test_admin_forms.py`` (create, edit, delete,
inlines carrying data, validation failures, a real JPEG upload driving
``PhotoForm.clean`` and the autoconnect signal), ``test_admin_changelist.py``
(field-name classes, sorting, fieldsets, ordering, per-admin stylesheet),
``test_templates.py`` (what the report pages actually render, including the
empty branches) and ``test_project_urls.py`` (root redirect, login/logout,
404, dashboard modules).

**245 tests, 98 % over both packages.** Everything is at 100 % except
``models.py`` (99 %) and the vendored ``kasvimuseo_admin_list.py`` (91 %),
which is still not tested directly by design.

Two stale comments
------------------

Both standing ``# FIXME`` comments in ``admin.py`` were wrong, and tests prove
it:

* ``# FIXME: action selection doesn't work`` -- "Create Species Sheets" driven
  through the changelist POST returns a 302 to ``/planted-species/22,11/``.
* ``# FIXME: filtering doesn't work`` (on SpeciesAdmin, ObservationAdmin and
  CareAdmin) -- every documented ``list_filter`` narrows the rows correctly,
  and the Grappelli filter pulldown renders working links.

All five of them -- the two texts appear on five lines -- are now deleted, and
``browser_tests/test_admin_changelist.py`` checks the two features in a real
browser as well, which is what a test client could not do. The browser is also
where the original complaint came from: Grappelli's own ``actions.js`` deletes
the admin's "Go" button and submits the changelist from the action dropdown's
``change`` event, so an action runs the instant it is chosen. See
``docs/issues/013``.

Where the findings live
-----------------------

Everything this work turned up is filed under ``docs/issues/``, one document
per actionable finding, with a status field to track the decision on each.
``docs/issues/README.rst`` indexes them and explains the convention. In short:
a broken placeholder image on every observation page, a search box disabled on
the public species list, a dead 165-line template, an unknown species id
rendering an empty page rather than a 404, the photologue gallery index raising
on an empty database, the labels API pairing items to labels by position, and
the report pages opening every image file just to pick a CSS class.

The last of those is the IOError-on-missing-media hazard the README warns
about: it comes from ``{{ page.species.photo.image.width }}`` in
``planted-species.html``, used both in a debug HTML comment and in a real
``horizontal``/``vertical`` class, so removing the comment alone does not
remove the file access. See ``docs/issues/011``.

The 626-line Vue label editor in ``planting-labels.html`` is covered only at
the server contract level -- 200, the mount point, the data endpoint URL and
the Vue script. Its real behaviour needs a browser, and has one since issue 017:
``browser_tests/``, run by ``dev/kasvimuseo app browser-test``. It is a separate
suite on a separate interpreter, so it adds nothing to the figures above.


Sequencing
==========

============ =========================================== ==================
Step         Contents                                    Depends on
============ =========================================== ==================
0            Infrastructure 1--6                         (none)
1            P1, plus defects 1 and 2                    0
2            P3 (independent; can land in parallel)      0
3            P2, plus defect 4                           0, 1
4            P4, plus defect 3                           0, 1
5            P5                                          0, 1
============ =========================================== ==================

Step 0 is a prerequisite for everything and is small -- one settings module,
one ``pytest.ini`` move, one factories module and two changes to
``dev/kasvimuseo``. It should land together with, or straight after, the
``dev-environment`` merge.
