=========================================================
Issue 036: The runtime stack is end-of-life and unpatched
=========================================================

:Status: Open
:Severity: High
:Area: platform / security
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: 016, 019, 020, 021, 022, 023, 024, 027, 028, 029, 030, 031, 032, 033, 034 -- the individual obstacles, listed by stage under Progress below
:Blocks: (none)
:Related: 035 -- the ceiling that will make this recur
    040 -- option 3 there is to wait for this
    038 -- most of the documentation build's workarounds fall away at Stage 10
    018 -- CI has to run the project's own container until Stage 10
:Decision: undecided
:Resolution: (none yet)

Problem
=======

The application runs on **Python 2.7** and **Django 1.5.1**.

* Python 2.7 reached end of life on 1 January 2020.
* Django 1.5 stopped receiving security support in 2014. The current release is
  6.0.7; the pinned version was 1.5.1, and even 1.5.12 -- the last patch in that
  series, with the security fixes -- had never been applied. Stage 1 applied it,
  so the pin is 1.5.12 now: the eleven patch releases are in, and the series is
  still eleven years past its last security fix.
* ``python:2.7-alpine``, the base image, has had no updates since 2020, which
  includes the C libraries it links against.
* ``psycopg2-binary``, ``Pillow`` and the rest are pinned at similarly old
  versions.

This is the umbrella issue for the whole modernisation. The work is planned in
detail in **``docs/upgrade-plan.rst``**: 20 stages, from removing dead
dependencies through to Django 6.0 on Python 3.12, with the constraints,
per-stage lock files and code changes each one forces.

Impact
======

Unpatched security vulnerabilities across the entire stack, in an application
that is on the public internet and holds an admin login. No individual CVE is
called out here because the surface is the whole runtime, not one component.

Beyond security: the project cannot use current tooling, cannot run on current
CI images, and every new dependency has to be checked for Python 2 support --
which almost nothing has any more.

Options
=======

Follow ``docs/upgrade-plan.rst``. Its structure, in brief:

============ ======================================================
Stages 0-1   Dead weight and defensive settings; Django 1.5.12
             -- **both done**, see Progress
Stages 2-4   photologue forward, still on Django 1.5/1.6
             -- **2 done** (2.6.1 to 2.8.3), see Progress
Stage 5      **South to Django migrations** -- the riskiest step
Stages 6-9   Django 1.7 to 1.11 LTS, the staging point
Stage 10     **Python 2.7 to 3.7** -- the irreversible one
Stages 11-19 Django 2.0 to 6.0, one version at a time
============ ======================================================

Suggested holding points are the LTS releases: 1.11 (before the Python flip),
2.2, 3.2, 4.2 and 5.2. Each is somewhere the project can sit indefinitely if
the work has to pause.

The effort is concentrated in four places: the South migration conversion
against real data, the Python 2 to 3 flip, the photologue ``title_slug`` rename
plus sites framework, and the recurring ``kasvimuseo_admin_list.py`` re-sync
(issue 034). Everything else is mechanical.

Progress
========

**Stages 0, 1 and 2 are done. This issue stays ``Open``:** three stages of
twenty, the application is still Python 2.7 and still unpatched everywhere but
Django, and nothing about that is finished. It closes when the programme does.

Stage 0 went in three changes. First, with 020, 021 and 033 ``Fixed``
together, the dead weight it lists went -- ``django-indexer``,
``django-paging`` and ``django-pserver`` uninstalled, ``gunicorn`` no longer an
app. That change is also the first evidence against this issue's own caveat
below: the container was built, the suite run and the pages rendered. Then
022's dead grappelli route went, and 031 vendored ``django-jqm`` into ``jqm/``
rather than fetching it from a GitHub URL, so no build reaches anywhere but
PyPI and the templates the later stages have to fix are in this repository.
The eighth and last item was ``django-extensions``: it is in
``requirements/dev.txt`` alone now, and ``local_settings.development.py``
rather than the shared ``common_settings.py`` is what puts it into
``INSTALLED_APPS``, so a production install has neither the package nor the
app entry.

Stage 1 is Django **1.5.1 → 1.5.12** -- the last release in the series, with
eleven releases' worth of security fixes that had never been applied: the
``reverse()`` code-execution fix, the ``contrib.admin`` ``to_field`` data
leak, two ``is_safe_url`` redirect fixes, the session-serializer setting, the
cache/``Vary`` fixes and the rest. One line in the lock; nothing else in the
repository names a Django version. The Problem section above still describes
1.5 as unpatched -- for the Django line specifically, it is not any more,
though 1.5 as a *series* has had no security support since 2014, which is
what makes the rest of this plan necessary.

Stage 2 is **photologue 2.6.1 → 2.8.3**, moved alone and still on Django 1.5,
because photologue owns database tables and must not move in the same step as
the framework. It renames ``Photo.title_slug`` to ``Photo.slug``, gives
``Photo`` and ``Gallery`` a ``sites`` many-to-many -- so
``django.contrib.sites`` is installed and ``SITE_ID`` is 1 now, neither of
which this project had -- and brings ``django-sortedm2m==0.7.0`` and
``django-model-utils==2.3.1`` into the lock. ``SOUTH_MIGRATION_MODULES`` and
``ylaneenkasvit/external_migrations/photologue/`` are gone with it: photologue
runs its own migration history again, and the sequence that gets an existing
database there is ``dev/kasvimuseo db upgrade-photologue``, written down as a
command because it is what production will have to be given.

All three stages were tested the way the caveat below asks for; see the next
section for exactly what was run and what it found.

Three further obstacles are out of the way: 019 is ``Fixed``, so
``MIDDLEWARE_CLASSES`` is now written out in ``common_settings`` and Stage 11
has a list to rename rather than an absence to notice; 023 is ``Fixed`` with it,
so ``django.contrib.messages`` is installed and Stage 5 will not meet an admin
system check it fails; and 016 is ``Fixed``, so Stage 10's source work no longer
includes the ``filter()`` that would have corrupted every derived photo slug.
This issue tracks the programme; the individual obstacles have their own issues:

============ ===========================================================
Issue        Blocks or complicates
============ ===========================================================
020/021/033  Dead apps and pins -- fixed; Stage 0 has three items less
019          MIDDLEWARE -- fixed; Stage 8 renames an explicit list
023          contrib.messages -- fixed; the app is installed for Stage 5
024          ``TEMPLATE_DIRS`` path -- fixed; Stage 10 has one item less
016          ``remove_diacritics`` -- fixed; Stage 10 has nothing to do here
027          No upper bounds -- every stage needs a real lock
028, 029     Pillow and setuptools ceilings on specific stages
030          Early stages need a period-appropriate build image
031          URL dependency -- fixed; Stage 0 has one item less
034          Recurring cost at all 19 Django steps; decide before Stage 6
035          The ceiling that will cause this to recur
============ ===========================================================

What is verified, and what is not
==================================

Verified: the constraints between packages, and that the far end works --
Django 6.0.7 with grappelli 5.0.0 and photologue 3.20 starts, passes
``manage.py check`` and has no pending migrations, as does the Django 5.2
equivalent.

**Not** verified: any of it against this project's own code or database.
``podman`` was unavailable when this was written, so the container was never
built, no migration was run and no page was rendered. Stage 0 should be treated
as a test of the reasoning, not as a foregone conclusion.

Its first three items have now had that test, and it was worth running: the
container was rebuilt without the removed packages, the suite passed, the
production dump was restored and migrated forward and the pages were rendered
over HTTP -- and the reasoning turned out to be wrong in one place. 020 claimed
the two apps carried no models and no migrations; ``django-indexer`` carries
both, and the table it created is in the production database. Harmless, and
recorded in 020 rather than discovered later.

Stage 0's last item and Stage 1 have had the same test, in one pull request.
What was run, on both changes:

* ``dev/kasvimuseo app test`` -- 430 passed, twice: once on the
  django-extensions change alone and once on Django 1.5.12.
* ``dev/kasvimuseo app browser-test`` -- 25 passed, the label editor in
  Chromium against a gunicorn-served instance of both changes together.
* ``dev/kasvimuseo app manage validate`` -- 0 errors (1.5's ``check``), with
  ``django_extensions`` appended by the development settings and
  ``runserver_plus`` still reachable through ``app manage``.
* The development image rebuilt from the changed requirements, and the
  production ``Dockerfile`` image built from the changed lock -- seven runtime
  packages -- ``validate``\ d and then started under gunicorn against the
  restored database, serving the public species list, the admin and the login
  page.
* ``.dev/backups/production.sql`` restored and ``migrate`` run forward on
  1.5.12 -- three ``kasvimuseo`` migrations applied, initial data loaded,
  photologue already current.
* Pages rendered over HTTP against that restored database, logged in: the
  admin index, the species and planting changelists, a species change form,
  the photologue photo changelist, the user changelist, the label editor, the
  public planted-species list, the printable and compact species reports and
  an observation page. All 200, and the admin chrome Finnish.
* ``dev/kasvimuseo docs`` clean.

Four things the reasoning had not predicted, all recorded where the wrong
claim was rather than fixed quietly:

#. ``dev/Containerfile`` installed ``production.txt``, so taking a package out
   of the production lock took it out of the *development* image. The
   development image installs ``dev.txt`` now.
#. ``six`` was in the production lock only because django-extensions declares
   it -- measured in the built image, where django-extensions is the only
   distribution that declares or imports it -- so it followed that package
   into ``dev.txt``. The plan had ``six`` down as Stage 10 work for the wrong
   reason.
#. The production ``Dockerfile`` copies the untracked
   ``ylaneenkasvit/local_settings.py`` of whatever checkout builds it into the
   image -- ``DEBUG = True`` and an open ``ALLOWED_HOSTS`` in a production
   image, silently, since that file has existed. Stage 0 turned it loud (an
   ``ImportError`` for an app the production image no longer installs) and
   ``.containerignore`` now excludes it.
#. Issue 040's packaging accident **is fixed by Stage 1**. Django 1.5.12 ships
   its locale catalogs as ``package_data``; 1.5.1 shipped them as
   ``data_files``, which is the whole of 040. Verified on the rebuilt image:
   no stray ``/usr/local/django``, both ``fi`` catalogs inside the package,
   admin chrome Finnish. 040's "option 3 -- wait for the upgrade" needed only
   one stage, not twenty. Its workaround stays in both image definitions as an
   assertion.

Stage 2 has had the same test, and it is the first stage where the test
changed the change. What was run:

* ``dev/kasvimuseo app test`` -- **432 passed**: the 430 of Stage 1 plus the
  two regression tests this stage needed. Four test modules and
  ``browser_tests/seed.py`` moved from ``title_slug`` to ``slug`` with the
  code.
* ``dev/kasvimuseo app browser-test`` -- **29 passed**, the label editor and
  the admin changelist in Chromium. The 25 recorded above is Stage 1's number
  and neither of the four tests between them is this stage's: issue 013 added
  ``browser_tests/test_admin_changelist.py`` and issue 056 added two to the
  label editor.
* ``dev/kasvimuseo app manage validate`` -- 0 errors, with
  ``django.contrib.sites``, ``sortedm2m`` and photologue 2.8.3 installed.
* Both images rebuilt from the changed lock: the development image
  (``dev.txt``) and the production image (``Dockerfile``, ``production.txt``),
  the latter carrying eleven runtime packages and, checked inside it, no
  ``ylaneenkasvit/local_settings.py``.
* ``.dev/backups/production.sql`` restored and ``dev/kasvimuseo db
  upgrade-photologue`` run on it, then the same command's parts inspected in
  ``psql``: 137 photos and one gallery on site 1, the four gallery photos
  given sort values 0-3, every title unchanged, and ``photologue_photo.slug``
  where ``title_slug`` was.
* ``dev/kasvimuseo db bootstrap`` on an empty database as well, since this
  stage changes what a fresh database is built from: photologue's own
  ``0004_initial_photosizes`` now runs before ``initial_data.json``, and the
  four photo sizes that come out are still the fixture's.
* Pages rendered over HTTP against the restored database, logged in: the admin
  index, the species and planting changelists, a species change form, the
  photologue photo changelist **and a photo change form** -- which is where the
  renamed field shows -- the photologue gallery admin, the public gallery
  index, the label editor, the public planted-species list, the printable and
  compact species reports and an observation page. All 200.
* ``dev/kasvimuseo docs`` clean, and ``actionlint`` on
  ``.github/workflows/tests.yml``, which is unchanged by this stage and does
  cover the browser suite -- ``playwright`` is a job of its own beside
  ``pytest``, ``sphinx`` and the Pages deploy.

Four more things the reasoning had not predicted, all recorded where the wrong
claim was:

#. **photologue 2.8.3 does declare its new dependencies**, against what
   ``requirements/production.txt`` said beside the absent package: its
   ``requirements.txt`` is read into ``install_requires`` and asks for
   ``django-sortedm2m>=0.6.1,<0.8`` and ``django-model-utils>=2.0.3``. The
   plan asked for sortedm2m 1.1.1 or later; 1.5.0 was installed and run first,
   and two things sent it back under the declared ceiling to 0.7.0. The
   decisive one is that a declared requirement is enforced at *runtime* in the
   production image: ``manage`` there is a setuptools console script, which
   resolves every distribution's declared requirements through
   ``pkg_resources`` before running, so ``manage validate`` and ``manage
   migrate`` both died with ``ContextualVersionConflict``. The development
   image cannot show this, because the same commands run as ``python
   ylaneenkasvit/manage.py``, and neither can the suite.
#. **``django-model-utils`` has a ceiling nobody declares.** photologue imports
   ``model_utils.managers.PassThroughManager`` and 2.4 deleted the class, so
   2.3.1 is the last usable release. That is issue 027's thesis arriving twice
   in one stage.
#. **The plan's migration recipe was wrong twice.** No ``--fake`` back to
   ``0001`` is needed -- the local squashed migration *is* photologue's own
   ``0001_initial`` -- while ``0002``, which the plan did not mention, must be
   faked, because its data half renames every photo in the database rather
   than only the ones with over-long titles. And ``kasvimuseo``'s own
   migrations have to be finished first: ``kasvimuseo:0021`` reads
   ``species.photo`` through a frozen ORM that still has ``title_slug``.
#. **Three packages do not compose on Django 1.5**, which is the other reason
   for that pin and the one that would have shipped a broken public page.
   photologue 2.8's default manager (``django-model-utils``) and its
   ``Gallery.photos`` field (``django-sortedm2m`` 1.x) together lose the filter
   that makes a related manager related, so ``gallery.photos`` is every photo
   in the database and ``/photologue/gallery/`` is a 500 -- on a database that
   has one real gallery with four photos in it. sortedm2m 0.7.0 does not have
   the branch that causes it. ``kasvimuseo/tests/test_photologue_galleries.py``
   pins both symptoms, so raising the pin while this project is still on
   Django 1.5 fails there; Stage 3 makes the branch correct and Stage 6 drops
   ``django-model-utils``.

One more thing the rendering turned up, which belongs to neither stage: in the
production image ``/photologue/gallery/`` is a 500, because that image ships no
``ylaneenkasvit/templates/`` and the page extends ``base.html``. An image built
from this repository before this branch has the same gap, so it is older than
both changes and is reported in :doc:`incoming` rather than fixed here.

And one thing that was predicted and held: Stage 1 really is "no API change"
for this project. The only settings difference between 1.5.1 and 1.5.12 is a
new ``SESSION_SERIALIZER`` that defaults to the old behaviour; the removals
(``WSGIServerException``, ``fix_IE_for_*``) are not imported here; the
``reverse()`` restriction does not bite because every reversal here names a
URL pattern; and the ``to_field`` restriction was exercised on the running
instance -- ``/admin/auth/user/?pop=1&t=password`` now raises
``DisallowedModelAdminToField``, which is the point of the fix, while every
admin page this application uses still renders.
