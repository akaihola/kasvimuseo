Incoming issues to be split into individual files
=================================================

Write new reports here in whatever shape they arrive -- a sentence is enough --
and they get split into numbered files under ``docs/issues/`` with the causes
traced as far as they go.

Waiting
-------

* **The species list page names a photo size that is not in the initial data.**
  ``reports/planted-species-list.html`` renders
  ``species.photo.get_mobilethumbnail_url``, but
  ``ylaneenkasvit/fixtures/initial_data.json`` defines only
  ``admin_thumbnail``, ``thumbnail`` and ``display``. Photologue attaches
  ``get_<size>_url`` only for sizes that are in the database, so where that row
  is missing the accessor does not exist, the template renders ``src=""``, and
  the list shows a broken image for every species. Found while covering
  :doc:`011 <011-species-report-opens-every-image-file-to-pick-a-css-class>`,
  whose test had to create the size to have a photo to assert about. Whether
  production is affected is exactly the open question: ``initial_data.json`` is
  loaded at ``syncdb``, so a ``mobilethumbnail`` row added by hand years ago
  would be in the production database and in no dump this repository has. It
  needs one ``SELECT name FROM photologue_photosize`` on the server before it
  is worth a number -- if the row is there, the fix is a line of fixture so a
  fresh database matches; if it is not, it is also a visible defect in
  production.

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
