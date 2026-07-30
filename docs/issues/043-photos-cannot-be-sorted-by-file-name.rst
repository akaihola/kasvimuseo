=========================================================
Issue 043: The photo changelist cannot be sorted by name
=========================================================

:Status: Fixed
:Severity: Low
:Area: admin / photos
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: ``kasvimuseo/tests/test_admin_changelist.py`` --
    ``test_photo_changelist_file_name_header_is_a_sort_link`` and
    ``test_photo_changelist_sorting_orders_the_rows`` now pin the fixed
    behaviour, next to the column test that pinned the old one
:Depends on: (none)
:Blocks: (none)
:Related: 003 -- the same photo file names, seen from the matching side
:Decision: ``image_filename.admin_order_field = 'image'``. Case is left to the
    database rather than forced to lower case, and the ordering assumes every
    photo stays in one directory; both are argued in "Decision" below.
:Resolution: Fixed in ee08991.

Problem
=======

On ``/admin/photologue/photo/`` every column is a sort link except the first
one, the file name -- the column this project added. ``PhotoAdmin`` replaces
photologue's ``title`` column with its own::

    class PhotoAdmin(PhotologuePhotoAdmin):
        list_display = ['image_filename' if field_name == 'title' else field_name
                        for field_name in PhotologuePhotoAdmin.list_display]

        def image_filename(self, obj):
            return obj.image.name.split('/')[-1]

``image_filename`` is a ``ModelAdmin`` method, and Django only makes a column
sortable when it can name a database column for it. The rendered header shows
the difference exactly::

    <th class="fieldname_image_filename"><span>Image filename</span></th>
    <th class="sortable fieldname_date_taken"><a href="?o=2.-3">Date taken</a></th>

So date taken, date added, is public, tags and view count sort; file name and
the thumbnail do not.

Impact
======

Photos are found by file name -- that is why the column replaced photologue's
``title`` in the first place -- and it is the one column that cannot be used to
order the list. With one flat upload directory holding every photo the site has
ever had, that is the difference between finding a picture and scrolling for it.

Options
=======

It is possible, and it is one line. Every photo is stored flat under
``photologue/photos/`` (photologue's ``get_storage_path`` joins
``PHOTOLOGUE_DIR``, ``'photos'`` and the file name), so the ``image`` column is
the file name with a constant prefix, and ordering by it is ordering by name::

    image_filename.admin_order_field = 'image'

Two things to decide while doing it:

1. **Case.** The sort is the database's, not Python's. On PostgreSQL with a
   Finnish locale ``Kuva.jpg`` and ``kuva.jpg`` sort together; on a ``C``
   collation they do not. Issue 003 is the same case-sensitivity question about
   the same file names seen from the matching side.
2. **The prefix.** Sorting by ``image`` also sorts by directory. That is a
   no-op today because there is only one directory, and it stops being a no-op
   if ``PHOTOLOGUE_DIR`` or ``get_storage_path`` ever changes.

The reporter asks for this one to be done rather than decided: research whether
it is possible (it is -- above), write a plan, implement it red/green with a
test that asserts the header carries a sort link and that ``?o=`` orders the
rows, and document it. Work in a worktree.

Decision
========

The one line, on ``PhotoAdmin.image_filename`` in ``kasvimuseo/admin.py``. The
two sub-decisions it needed:

**Case: left to the database.** The two clusters this project runs on do not
agree, and the one the maintainer actually sorts photos on already does the
right thing:

* production creates ``ylaneenkasvit`` through ``geerlingguy.postgresql``, and
  ``ansible/vars/main.yml`` sets no ``lc_collate``, so it takes the role's
  default ``en_US.UTF-8`` (``roles/geerlingguy.postgresql/tasks/databases.yml``).
  Under that collation case is not the first thing compared, so ``Kuva.jpg``
  and ``kuva.jpg`` land together, which is what somebody looking for a file
  wants.
* the development cluster is ``initdb --locale=C.UTF-8``
  (``dev/kasvimuseo``, ``db_init``), which is byte order: every upper-case
  initial sorts before every lower-case one.

Forcing case-insensitivity would mean ordering by ``lower(image)``, and on
Django 1.5 -- no ``Lower()`` before 1.8 -- that is a ``queryset()`` override
adding ``.extra(select={...})`` and an ``admin_order_field`` naming the alias:
several lines of version-specific code, and a sort no index can serve, to
change nothing in production and only tidy a local cluster's dumps. So: not
forced. The tests order lower-case file names only, so they pass under either
collation, and the divergence is written down here rather than fixed silently
in one of the two places.

This is consistent with issue 003, which normalises case in Python and, for the
one comparison that has to be a query, asks for it with ``iexact``, and the
reason the answers take different shapes is the operation, not the data. 003
compares for **equality**, and no PostgreSQL collation folds case for
equality -- ``'Kuva' = 'kuva'`` is false under ``en_US.UTF-8`` as much as under
``C`` -- so a match that must ignore case has to say so itself. Ordering is the
one place the collation already does it. Both answers say the same thing: case
must not decide whether the user finds the photo.

**The prefix: the fix assumes one directory.** Ordering by ``image`` orders by
the whole stored path, directory first, and it is ordering by file name only
because photologue's ``get_storage_path`` puts every photo in exactly one
directory, ``photologue/photos/``. That holds for the installed photologue
2.6.1 and for the production media tree. If ``PHOTOLOGUE_DIR`` changes, or
photologue ever grows per-gallery or per-date subdirectories, the column
silently becomes "sort by directory, then by name" -- the same rows, grouped
wrong, with nothing failing. The suite would not catch it either: its photos
all land in one directory too. That is the assumption this fix rests on, and
the note is the whole mitigation; the alternative -- storing the base name in
its own indexed column -- is not worth it for a one-directory installation.

Resolution
==========

``kasvimuseo/admin.py`` sets ``image_filename.admin_order_field = 'image'``,
and ``kasvimuseo/tests/test_admin_changelist.py`` gains two tests beside
``test_photo_changelist_shows_the_file_name``: the header now carries the
``sortable`` class and an ``?o=`` link, and following that link orders the rows
by file name in both directions. Both failed before the attribute and pass
after it. Commit ee08991.

See also
========

Issue 003 (photo-to-species matching is case-sensitive): the same file names,
and the same question about case, decided at the other end of the same data.
