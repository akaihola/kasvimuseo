====================================================================
Issue 011: Species report opens every image file to pick a CSS class
====================================================================

:Status: Fixed
:Severity: Medium
:Area: templates / operations
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py (uses real JPEG fixtures for these views)
:Depends on: (none)
:Blocks: (none)
:Related: 004 -- option 2 there depends on how the species photo is rendered; 006 -- the dead template carried the same expression
:Decision: Option 1, store the orientation. Option 2 does not exist in the pinned photologue: 2.6.1's ``ImageModel`` keeps no dimensions on the model at all, and its one size accessor, ``_get_SIZE_size``, is ``Image.open(self._get_SIZE_filename(size)).size`` after a ``create_size`` that opens the original when the cached copy is absent -- a file open either way. So ``Species.photo_is_horizontal`` plus a South migration and a backfill. Fallback when the file cannot be read is ``vertical``, because that is the branch the template already took for a species with no photo, so nothing that renders today changes shape.
:Resolution: 93a191e -- ``Species.photo_is_horizontal`` and ``measure_photo_orientation()``, migrations 0020 (column) and 0021 (backfill), both report templates, and the tests that prove no image file is opened.

Problem
=======

``reports/planted-species.html`` reads image dimensions in two places::

    <div class="header {% if page.species.photo.image.width > page.species.photo.image.height %}horizontal{% else %}vertical{% endif %}">
        <div class="photo"><!-- {{ page.species.photo.image.width }}x{{ page.species.photo.image.height }} -->

Reading ``.width``/``.height`` makes Django open the file. The second use is a debug
comment, but the first is a real ``horizontal``/``vertical`` class, so **removing the
comment alone does not remove the file access**.

This is the cause of the ``IOError`` the README warns about, and why
``dev/kasvimuseo media fetch`` exists: the printable and compact reports need the actual
image files present, not just a ``MEDIA_URL``.

Impact
======

Reports break with IOError when media is missing, and open every referenced image on every render when it is not.

Options
=======

1. Store the orientation on the ``Photo``/``Species`` when the image is uploaded, and
   render from that -- no file access at render time.
2. Use photologue's cached display size if it exposes one without opening the original.
3. Delete the debug comment regardless; it is redundant with the class.

3 was done unconditionally. 2 was checked against the installed version and
does not exist, so 1 was taken. See ``Decision`` above and the sections below.


Why option 2 does not exist
===========================

``requirements/production.txt`` pins ``django-photologue==2.6.1``, and that is
the code the answer has to come from rather than upstream's current source.
In 2.6.1 ``photologue/models.py``:

* ``ImageModel`` declares ``image``, ``date_taken``, ``view_count``,
  ``crop_from`` and ``effect``. No width, no height, and the ``ImageField``
  is declared without ``width_field``/``height_field``, so Django stores
  nothing either. There is no dimension anywhere in the database to read.
* The sized-variant accessors ``add_accessor_methods`` attaches are
  ``get_<size>_size``, ``get_<size>_url``, ``get_<size>_filename`` and
  ``get_<size>_photosize``. ``get_<size>_photosize`` returns the ``PhotoSize``
  row -- the size that was *asked for*, 352x352 for ``display``, not the shape
  of this photo. ``get_<size>_size`` is the one that answers the real question,
  and it is ``Image.open(self._get_SIZE_filename(size)).size``: a file open,
  preceded by ``create_size`` -- which opens the *original* -- whenever the
  cached copy is not there yet.

So every route photologue offers ends in an open. Storing the orientation is
the only way to stop opening files at render time.


What was done
=============

* ``Species.photo_is_horizontal``, a ``NullBooleanField``, written by
  ``Species.save()`` through ``measure_photo_orientation()`` -- the one place
  left that measures an image. Every route that changes ``Species.photo`` ends
  at ``save()``, including ``autoconnect_photo_to_species``, which fires when
  the file behind an already attached photo is replaced, so the stored value
  cannot go stale.
* ``0020_auto__add_field_species_photo_is_horizontal`` adds the column and
  ``0021_backfill_species_photo_is_horizontal`` measures the existing rows.
  Both were applied to the production dump itself, restored with
  ``dev/kasvimuseo db restore`` and standing at 0019 with no such column: 156
  species, 113 of them with a photo. The backfill measured **93 horizontal and
  20 vertical**, leaving ``NULL`` on exactly the 43 that have no photo, and
  re-reading all 113 files afterwards and comparing found **113 matches and no
  mismatches**. Run once with the media directory absent it filled nothing and
  failed nothing, which is the other half of the promise. Both reports were
  then rendered from that database, one species from each branch, and each came
  back 200 with the right class.
* The two templates render ``{% if ...photo_is_horizontal %}``, and the debug
  comment is gone. ``planted-species-compact.html`` carried the same
  expression and was fixed with them; it is the dead template of issue 006, so
  deleting it later removes a copy of this rather than un-fixing anything.

**The fallback is** ``vertical``. ``NULL`` means "not measured": no photo, no
file behind the photo, or a file that could not be read. The template treats it
exactly as it treated a species with no photo before this change, which is what
``test_printable_sheet_renders_a_bare_species_cleanly`` already pinned, so a
report renders instead of raising and nothing that worked before changes shape.
A row measured while its file existed keeps its orientation when the file goes
away, and a row that could not be measured is filled in the next time it is
saved or the backfill is run.


Evidence that the file access is gone
=====================================

``test_reports_open_no_image_file`` renders all three reports that put a photo
on the page -- the printable sheet, the compact sheet and the species list --
with ``PIL.Image.open`` and ``FileSystemStorage._open`` instrumented. Those are
the two doors an image can come through, since Django reads
``ImageFieldFile.width`` via the storage and photologue builds its cached sizes
via PIL on the path, and patching one alone would prove nothing. It fails on the
old template, with the original JPEG named in the list.
``test_compact_sheet_header_class_follows_the_photo_shape`` and
``test_printable_sheet_uses_the_vertical_header_for_a_portrait_photo`` cover
both orientations, and ``test_reports_render_when_the_image_file_is_missing``
covers the ``IOError``.

One open survives, and it is not this issue: the first request for a photo whose
cached copy at that size has never been built still opens the original, in
photologue's ``create_size``, because every shipped ``PhotoSize`` has
``pre_cache`` off. That is once per photo and size, ever, rather than once per
render, and the test warms it before it measures -- then asserts the warm-up
*did* open something, so the test cannot quietly become vacuous if a page stops
rendering its photo. Turning ``pre_cache`` on would move even that to upload
time; it is a data change, not a code one, and was left alone.

Covering the list page turned up something that is not this issue either and is
in :doc:`incoming`: it renders ``get_mobilethumbnail_url``, and no
``mobilethumbnail`` ``PhotoSize`` is in ``initial_data.json``, so on any
database built from that fixture the accessor does not exist and the page shows
a broken image. The test creates the size rather than working around its
absence, which is why it is a test of file access rather than a test of nothing.


Consequences elsewhere
======================

``dev/kasvimuseo media fetch`` is no longer needed to *browse* the reports --
``README.rst`` said it was, and now says what it is actually for. It is still
what makes the photos visible rather than redirected, and running it before
``0021`` is what gets the orientations measured in one pass.

Issue 004's option 2 -- rendering the observation page's real photo -- was
deferred pending how the species photo is rendered, which is this. The answer
for it: the orientation of a species photo is now a stored field, so a template
that wants one asks ``species.photo_is_horizontal`` and never the image. A
photo reached any other way, including ``PlantingPhoto.photo``, has no such
field and would reintroduce exactly this defect if it read ``.width``. Nothing
was implemented for 004 here.
