==================================================================
Issue 054: The species list names a photo size not in the fixtures
==================================================================

:Status: Fixed
:Severity: Low
:Area: fixtures / public site
:Reported: 2026-07-31
:Source: Covering issue 011's third report, commit a235a9c -- written into
    ``incoming.rst`` rather than given a number, because the one thing that
    fixed its scope was the state of the production database
:Evidence: kasvimuseo/tests/test_templates.py --
    ``test_the_initial_data_defines_the_mobilethumbnail_photo_size`` and
    ``test_species_list_renders_a_photo_url_from_the_fixtures_alone`` pin the
    fixed behaviour; before the fix the suite had a
    ``mobile_thumbnail_size`` fixture that created the row so that
    ``test_reports_open_no_image_file`` had a photo to be about at all
:Depends on: (none)
:Blocks: (none)
:Related: 011 -- found while covering it, and its test carried the workaround; 004 -- the other broken-image issue on a public page, Fixed
:Decision: Production is not affected, and the dump says so rather than the maintainer: ``photologue_photosize`` in ``.dev/backups/production.sql`` holds four rows, and the fourth is ``mobilethumbnail`` at 80x45, quality 80, ``crop`` and ``upscale`` on. So this is a fixture gap, not a live defect: the row was added on the server by hand and never written back. Option 1 plus option 2 -- the row goes into ``initial_data.json`` with the production values, so a fresh database matches the server, and a South data migration gives it to the databases that already exist, since ``initial_data.json`` is loaded at ``syncdb`` and never again. Option 3, pointing the template at ``thumbnail``, is rejected: it would change what production serves, which is the one thing here that is currently correct. Nothing had to be invented, so the question of what size to choose does not arise.
:Resolution: 6f6d20b -- the fixture row, migration ``0022_add_mobilethumbnail_photo_size``, and the two tests. The suite's ``mobile_thumbnail_size`` fixture is deleted with it.

Problem
=======

``kasvimuseo/templates/kasvimuseo/reports/planted-species-list.html`` line 29
renders::

    <img src="{{ species.photo.get_mobilethumbnail_url }}" />

``ylaneenkasvit/fixtures/initial_data.json`` contained exactly three
``photologue.photosize`` rows -- ``admin_thumbnail`` (51x36), ``thumbnail``
(128x128) and ``display`` (352x352). There was no ``mobilethumbnail``.

Photologue attaches ``get_<size>_url`` from ``PhotoSizeCache`` at
``post_init``, and only for the sizes that are rows in
``photologue_photosize``. Where the row is missing the accessor does not
exist; Django 1.5 resolves an unknown template variable to
``TEMPLATE_STRING_IF_INVALID``, which this project leaves at the empty string,
so the page renders ``src=""`` and answers 200. Nothing raises anywhere.

Impact
======

On a database built from ``initial_data.json`` alone -- a fresh checkout, a
new installation, CI -- every row of the mobile species list shows a broken
image. Production is unaffected: it has the row.

The severity is ``Low`` for that reason and no other. The rendered defect is
the same one 004 describes and would be ``Medium`` if a visitor could see it;
what caps it is that the only databases that lack the row are ones this
repository builds.

Options
=======

1. Add the ``mobilethumbnail`` row to ``initial_data.json`` so a fresh
   database matches production.
2. Also give it to databases that already exist, with a data migration --
   ``initial_data.json`` is applied at ``syncdb``, so an established
   installation never picks a new row up.
3. Point the template at ``thumbnail``, a size the fixture already has, and
   add nothing.
4. Nothing: it is invisible to users, so leave the development databases
   broken.

Decision
========

See ``Decision`` above. The reasoning, in the order it was worked out:

**The dump settled the scope, and no question had to be asked.** Issue 050's
precedent is that ``.dev/backups/production.sql`` can answer questions about
the server, and it answers this one exactly. Its
``photologue_photosize`` ``COPY`` block is::

    1  admin_thumbnail   51   36  70  f  t  f  f
    2  thumbnail        128  128  70  f  f  f  f
    3  display          352  352  70  f  f  f  f
    4  mobilethumbnail   80   45  80  t  t  f  f

-- ``id, name, width, height, quality, upscale, crop, pre_cache,
increment_count``, and the sequence is set to 4. The row is there. So the
report's second branch -- "it is also a visible defect in production" -- is
closed, and this is a repository-side fixture gap alone.

**That also answers what the size should be.** The report asked what to
invent if it had to be invented; it does not have to be. 80x45 is 16:9 at
thumbnail scale, cropped and upscaled so that every list row is the same
rectangle whatever shape the photograph is, at quality 80 rather than the 70
the other three use, which is the only place any of the four differ from
photologue 2.6.1's own field defaults. ``pre_cache`` is off, as it is on all
three of the others, so the cached copy is built on the first request for it
rather than at upload -- the one image open that 011's evidence section says
survives. ``effect`` and ``watermark`` are null. Those are the values, read
off the server rather than chosen.

**Option 3 is the one that would have done harm.** Pointing the template at
``thumbnail`` costs nothing on a fresh database and silently changes what the
public site serves on the only database that matters: 128x128 uncropped
instead of an 80x45 crop, so every row of the live list would change shape.
The fixture is the thing that is wrong here, not the template.

**Option 4 is rejected because the cost of the row is one line.** It is also
what the suite was already paying: the ``mobile_thumbnail_size`` fixture
existed only to create the row so that a test about the list page had a photo
to be about.

Resolution
==========

* ``ylaneenkasvit/fixtures/initial_data.json`` gains the fourth
  ``photologue.photosize`` row, at ``pk`` 4 with the production values, so a
  database built from it is identical to the server's in this table.
* ``kasvimuseo/migrations/0022_add_mobilethumbnail_photo_size.py`` is a South
  data migration doing ``get_or_create`` on the same values. **On production it
  does nothing**, which is the point -- the databases that need it are the ones
  built from the fixture before this change, including any developer's. It
  imports ``photologue.models.PhotoSize`` rather than taking it from ``orm``,
  because the row belongs to another application and no schema is being
  altered. Its ``backwards`` is deliberately empty: deleting the row would
  break the page on every database, including the ones that had it first.
* ``kasvimuseo/tests/test_templates.py`` gains
  ``test_the_initial_data_defines_the_mobilethumbnail_photo_size``, which
  asserts the shipped data rather than anything the suite arranges, and
  ``test_species_list_renders_a_photo_url_from_the_fixtures_alone``, which
  renders the page for a species with a photo and asserts the ``src`` is the
  real accessor's URL and not ``""``. The second is the regression test the
  report asked for: an empty ``src`` is exactly the failure, and Django's
  template layer will not raise on it.
* ``kasvimuseo/tests/conftest.py`` loses the ``mobile_thumbnail_size``
  fixture, and ``test_reports_open_no_image_file`` loses its argument. That
  test now reaches the list page's photo through the shipped data, and its
  existing warm-up assertion -- that rendering the page opened *something* --
  fails if the row ever goes missing again.

**Verified in the running application, not only in the suite.** On a database
built by ``dev/kasvimuseo db bootstrap``, with one species, one planting and
one uploaded photograph, ``/kasvimuseo/planted-species/`` renders::

    <img src="/media/photologue/photos/cache/valkonarsissi-kukassa_mobilethumbnail.jpg" />

and that URL answers 200 with 309 bytes of ``image/jpeg`` measuring 80x45 --
photologue building the cached copy on the first request, as ``pre_cache: false``
says it should.

**That check found something that is not this issue**, and it is :doc:`055
<055-initial-data-never-reaches-a-bootstrapped-database>`: on the
``db bootstrap`` path ``initial_data.json`` is not
installed at all. ``syncdb`` loads it before South has created
``photologue_photosize`` and dies on the first row, and nothing loads it again,
so such a database has no ``display`` and no ``admin_thumbnail`` either. It is
why the row this issue adds reached the page above through the data migration
rather than through the fixture. The fixture entry is still the right half of
the fix -- it is what the test database and any future non-South build get --
but on that path the migration is doing all the work, and the three older sizes
have nobody doing theirs.

055 is fixed now, so that last sentence has stopped being true: the fixture
moved to ``kasvimuseo/fixtures/initial_data.json``, where South loads it after
``migrate``, and it is what puts all four sizes into a bootstrapped database.
The paths written above are the ones this issue's own change touched and are
left as they were; ``0022`` is unchanged and still correct, and it still runs
first, so what it creates the fixture then overwrites by primary key.

**An existing database needs the migration and nothing else.** ``syncdb``
loaded ``initial_data.json`` once, when the tables were created, so a running
installation does not pick the new row up from the fixture; ``dev/kasvimuseo
app manage migrate kasvimuseo`` is what gives it to one. Production's own
answer is that it already has the row and ``get_or_create`` will find it.
There is no manual step beyond the deploy that runs the migrations.
