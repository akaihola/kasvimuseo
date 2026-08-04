=======
Archive
=======

Text this project removed on purpose, and where to read it. Git holds the
content; this page holds the pointer, so that nobody has to search the log for
a document that no longer exists.

Each entry names a path, the commit that still contains the file at that path,
and why the text went. The commit is always one that is already on ``master``,
because ``master`` is never rewritten here. A commit made on a task branch does
not survive the rebase, which is the same hazard the ``:Resolution:`` fields
carry.

The line format is fixed, because the documentation build checks that every
pointer resolves. ``docs/issues/README.rst`` defines it.

Removed
=======

* ``docs/issues/incoming.rst`` @ ``88455a0`` -- the "Emptied on ..." entries,
  removed 2026-08-04. About 160 lines that told, in prose, what became of every
  report the page had ever held. Each of those reports is a numbered issue file
  now. Each issue file carries its own reasoning, so the entries were a second
  copy that nobody updated. Read the page at that commit to see them.
