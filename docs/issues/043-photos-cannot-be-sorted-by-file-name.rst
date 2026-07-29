=========================================================
Issue 043: The photo changelist cannot be sorted by name
=========================================================

:Status: Accepted
:Severity: Low
:Area: admin / photos
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: ``kasvimuseo/tests/test_admin_changelist.py`` asserts the columns, not their sort links
:Depends on: (none)
:Blocks: (none)
:Related: 003 -- the same photo file names, seen from the matching side
:Decision: Asked for as work rather than as a question when it was reported:
    research whether it is possible, plan it, implement it red/green, and
    document it, in a worktree. The two sub-decisions it needs -- collation and
    the path prefix -- are in "Options" and are the implementer's to make.
:Resolution: (none yet)

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

See also
========

Issue 003 (photo-to-species matching is case-sensitive): the same file names,
and the same question about case, decided at the other end of the same data.
