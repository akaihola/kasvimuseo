======================================================================
Issue 055: ``initial_data.json`` never reaches a bootstrapped database
======================================================================

:Status: Fixed
:Severity: Medium
:Area: fixtures / dev environment
:Reported: 2026-08-01
:Source: Checking issue 054 in the running application -- written into
    ``incoming.rst`` first, because what it needed before it was worth a
    number was a decision about where the three photologue rows belong
:Evidence: kasvimuseo/tests/test_fixtures_initial_data.py -- four tests
    pinning where the fixture lives and what is in it. They do **not**
    exercise the failure: the test database takes the
    ``SOUTH_TESTS_MIGRATE = False`` path, where ``syncdb`` creates every table
    at once and the fixture loads cleanly wherever it sits, which is why the
    suite never saw this. What they pin is the static property the two
    fixture loaders differ on -- the application the fixture belongs to has
    migrations. The bootstrap itself is verified by hand, below
:Depends on: (none)
:Blocks: (none)
:Related: 054 -- the same table, and the check that found this; 048 -- the
    other defect that is only ever seen on a development machine; 011 -- the
    species report, one of the pages that rendered ``src=""``
:Decision: The fixture moves to ``kasvimuseo/fixtures/initial_data.json`` -- option 2 of the three the report listed, "a fixture loaded after ``migrate`` rather than during ``syncdb``", in the one shape that needs nobody to remember anything: South loads a **migrated** application's initial data after migrating it, and ``kasvimuseo`` has migrations while ``ylaneenkasvit`` has none. The maintainer was asked with the three options and the evidence, and chose this one; the reasoning below is the argument that was put with the question. It removes the cause rather than the symptom -- ``syncdb`` never tries the fixture again, for any caller, so nothing has to pass ``--no-initial-data`` or run a ``loaddata`` afterwards, and a hand-built production installation is fixed by the same change as a developer's ``db bootstrap``. It keeps one source of truth: the rows the test database gets and the rows a migrated database gets are the same file, so the fixture cannot silently go stale on the migrated path again, which is the trap 054 fell into. And it repairs the databases that are already wrong, on the next ``migrate``, with no manual step. Option 1, a data migration for the three older sizes beside 054's ``0022``, was rejected because it leaves that trap in place and still needs the error suppressed separately; option 3, a documented ``loaddata`` step in ``db bootstrap``, because it fixes one script rather than the defect. Production is unaffected either way -- the dump has all four rows already, with these values.
:Resolution: 0b6b3e9 -- the fixture moves to ``kasvimuseo/fixtures/``, ``dev/kasvimuseo``'s two stale comments are corrected, and ``test_fixtures_initial_data.py`` pins where it lives. No change to ``0022``, which stays correct and idempotent.

Problem
=======

``dev/kasvimuseo db bootstrap`` builds a database from the migrations. On the
way it printed::

    DatabaseError: Problem installing fixture
    '/src/ylaneenkasvit/fixtures/initial_data.json': Could not load
    photologue.PhotoSize(pk=1): relation "photologue_photosize" does not exist

and the script carried a comment saying that this was "noise rather than a
failure" because "South loads the same fixture again after migrating". **Both
halves were wrong.** The fixture was not installed at all, and nothing loaded
it afterwards.

Two loaders can install an ``initial_data`` fixture in a project with South,
and they differ in when they run and what they look at:

* ``syncdb`` creates the tables of the applications that have **no**
  migrations, then loads their initial data. It runs before South has created
  anything.
* South loads a **migrated** application's initial data after migrating that
  application -- ``south/migration/migrators.py``,
  ``LoadInitialDataMigrator``, which overrides ``get_apps`` so that only the
  one application's ``fixtures/`` directory is searched.

The fixture lived in ``ylaneenkasvit``, a package with no migrations that
exists for no other reason -- its ``models.py`` was a docstring saying so, and
its ``INSTALLED_APPS`` entry said ``# for fixtures``. So it got the first
loader, at the one moment ``photologue_photosize`` did not exist yet, and the
second loader never looked at it: ``migrate photologue`` reported ``Installed
0 object(s) from 0 fixture(s)``, and so did ``migrate kasvimuseo``. photologue
2.6.1 ships no initial data of its own.

Impact
======

On a freshly bootstrapped database, before the fix::

     id |      name       | width | height | quality | upscale | crop
    ----+-----------------+-------+--------+---------+---------+------
      1 | mobilethumbnail |    80 |     45 |      80 | t       | t
    (1 row)

-- one row, and it is there only because 054's data migration
``0022_add_mobilethumbnail_photo_size`` writes it. ``display``,
``admin_thumbnail`` and ``thumbnail`` were missing.

Photologue attaches ``get_<size>_url`` at ``post_init`` and only for the sizes
that are rows in that table, so the accessors the templates name did not
exist, and Django 1.5 resolves an unknown template variable to
``TEMPLATE_STRING_IF_INVALID`` -- the empty string here. Measured on that
database, with one species, one planting and one photograph:

* ``/kasvimuseo/planted-species-printable/55/`` -- ``<img src="" />``, where
  the template names ``get_display_url``.
* ``/kasvimuseo/planted-species/`` -- the same, from
  ``get_mobilethumbnail_url``, on every row.
* ``/admin/photologue/photo/`` -- no thumbnail column at all, but photologue's
  fallback text in its place: *An "admin_thumbnail" photo size has not been
  defined.*

Both answer 200. Nothing raises anywhere, which is why this survived until
somebody looked at a page.

The severity is ``Medium`` rather than ``High`` because production is not
affected and cannot be: it has all four rows, and no deployment step here
rebuilds a database. What it cost was every database this repository builds --
a fresh checkout, a new installation, and the machine 054 was verified on.

Options
=======

The report named three and chose none.

1. A data migration, like 054's ``0022_add_mobilethumbnail_photo_size``, for
   the three older sizes.
2. A fixture loaded after ``migrate`` rather than during ``syncdb``.
3. A documented ``loaddata`` step in ``dev/kasvimuseo db bootstrap``.

Decision
========

See ``Decision`` above. The reasoning, in the order it was worked out:

**What is actually broken is where the file is, not what is in it.** The
fixture's contents are right -- 054 checked them against the production dump,
and ``.dev/backups/production.sql``'s ``photologue_photosize`` block is the
four rows the file names, at the same ids, with the sequence at 4. What is
wrong is that the only loader that ever sees it is the one that runs too
early. Option 2 moves it to a loader that runs late enough, and the move is
one ``git mv``: ``kasvimuseo`` has 22 migrations, so South loads
``kasvimuseo/fixtures/initial_data.json`` after running them, when
``photologue_photosize`` exists.

**It is the only one of the three that a hand-built installation gets.**
Nothing in ``ansible/install.yaml`` runs ``syncdb`` or ``migrate`` -- the
deployment installs code and runs ``collectstatic`` -- so the schema on a new
server is built by hand, by somebody typing the same two commands
``db bootstrap`` types. Option 3 fixes the script that person is not running.
Option 1 needs ``syncdb --no-initial-data`` beside it to stop the error, which
is another thing to type and another thing to forget.

**Option 1 also leaves the trap that produced 054.** A fixture that no
migrated database ever loads is a file whose next new row silently reaches the
test database and nothing else -- exactly how ``mobilethumbnail`` came to be
missing everywhere but the server. Under option 2 there is one file and both
paths read it.

**It repairs the databases that are already wrong.** ``initial_data.json`` is
loaded at ``syncdb`` and never again, which is why 054 needed a data migration
at all; a fixture South loads after every ``migrate`` has no such
one-shot-ness. Verified: on the bootstrapped database above, with the three
rows still missing, a plain ``dev/kasvimuseo app manage migrate`` reported
``Loading initial data for kasvimuseo. Installed 4 object(s) from 1
fixture(s)`` and the table came out as production's.

**It does not double-write 054's row, and the ordering was checked rather than
assumed.** ``0022`` does ``get_or_create(name='mobilethumbnail')`` and runs
*before* the fixture load, so on an empty table it inserts that row at id 1;
``loaddata`` then writes id 1 as ``admin_thumbnail``, 2 as ``thumbnail``, 3 as
``display`` and 4 as ``mobilethumbnail``, since a fixture with explicit
primary keys updates by id. The end state is the four rows at production's
ids with the sequence at 4, and there is one ``mobilethumbnail``. On a
database that already has all four the load is a no-op update, so it is
idempotent in the sense that matters. ``0022`` is left alone: it is still
correct, and any database that has run it and not this is repaired by the
fixture on its next ``migrate``.

**Production changes in no way.** The four rows are already there with these
values, and no playbook runs a migration, so nothing about this reaches the
server until somebody runs ``migrate`` there -- at which point it writes the
values that are already in the table.

Resolution
==========

* ``ylaneenkasvit/fixtures/initial_data.json`` moves to
  ``kasvimuseo/fixtures/initial_data.json``, unchanged. The now-empty
  ``ylaneenkasvit/fixtures/`` directory goes with it.
* ``ylaneenkasvit/models.py`` and the ``INSTALLED_APPS`` entry in
  ``ylaneenkasvit/common_settings.py`` both said the package was there for the
  fixtures. Neither is true now, and both say what is: the package stays
  installed for ``ylaneenkasvit/locale/``, which there is no ``LOCALE_PATHS``
  entry to find it by. It defines no models, and the suite asserts that.
* ``dev/kasvimuseo`` loses the comment calling the ``DatabaseError`` expected
  noise -- in ``db bootstrap`` and again in ``browser-test``, where it also
  claimed photologue's own initial data supplied ``display``. Both now say
  where the photo sizes come from. The ``;`` that let ``syncdb`` fail without
  stopping the run is a ``&&`` in both places, so a real failure there is a
  failure again.
* ``kasvimuseo/tests/test_fixtures_initial_data.py`` is new: the fixture is
  ``kasvimuseo``'s and no other installed application has one; every
  installed application that has an ``initial_data.json`` has migrations;
  ``ylaneenkasvit`` has neither fixtures nor migrations nor models; and the
  file itself ships the four photo sizes at production's ids.

  The second of those is the regression test, and it is written over every
  installed application rather than over ``kasvimuseo`` alone, because the
  defect is not "the file moved" but "the file is somewhere ``syncdb`` will
  try it".

**What the suite cannot tell you.** The test database is built with
``SOUTH_TESTS_MIGRATE = False``, so ``syncdb`` creates every table at once and
the fixture loads cleanly from wherever it sits -- before this change as well
as after. A test that only runs on that path proves nothing about
``db bootstrap``, which is why the tests above assert a static property
instead, and why the check below was done by hand.

**Verified on a bootstrapped database, not by reading the code.** With the
database dropped and rebuilt by ``dev/kasvimuseo db bootstrap``, the run
prints no ``DatabaseError``, reports ``Loading initial data for kasvimuseo.
Installed 4 object(s) from 1 fixture(s)``, and::

     id |      name       | width | height | quality | upscale | crop
    ----+-----------------+-------+--------+---------+---------+------
      1 | admin_thumbnail |    51 |     36 |      70 | f       | t
      2 | thumbnail       |   128 |    128 |      70 | f       | f
      3 | display         |   352 |    352 |      70 | f       | f
      4 | mobilethumbnail |    80 |     45 |      80 | t       | t
    (4 rows)

-- the production dump's table, row for row, with
``photologue_photosize_id_seq`` at 4 as production's is.

**And the pages, which is the half a table cannot show.** On that database,
with one species, one planting and one uploaded photograph, and logged into
the admin:

* ``/kasvimuseo/planted-species/`` renders
  ``/media/photologue/photos/cache/issue055-narsissi_1_mobilethumbnail.jpg``
* ``/kasvimuseo/planted-species-printable/55/`` renders
  ``/media/photologue/photos/cache/issue055-narsissi_1_display.jpg``
* ``/admin/photologue/photo/`` renders
  ``/media/photologue/photos/cache/issue055-narsissi_1_admin_thumbnail.jpg``

All three 200, none of them ``src=""``, and the admin no longer says the
``admin_thumbnail`` size is undefined. Deleting the three rows again and
re-rendering reproduces the old output exactly, which is what makes the table
above a measurement rather than a hope.

**The suite and CI.** ``dev/kasvimuseo app test`` passes, 430 tests, and
``dev/kasvimuseo app browser-test`` passes, 25. ``.github/workflows/tests.yml``
never runs ``db bootstrap``, so the pytest and sphinx jobs are untouched by
this; the ``playwright`` job is not, because ``app browser-test`` builds its
throwaway database with the same ``syncdb``-then-``migrate`` sequence and the
same comment. It is the one job this change could have broken, and it is green.
