======
Issues
======

Known problems, kept in the repository so they travel with the code and can be
reviewed in a diff. One file per issue, named ``NNN-short-slug.rst``, numbered
in the order they were filed and never reused.

The layout follows the decision-record convention used elsewhere in these
projects (``docs/adr/NNN-slug.md``): a numbered file, a title, and a metadata
block at the top whose ``Status`` field is the thing you actually track. The
metadata is written as a reStructuredText docinfo field list rather than YAML
front matter, because the rest of this repository's documentation is
reStructuredText and docinfo is its native mechanism for exactly this.


Metadata fields
===============

``Status``
    ``Open`` -- filed, no decision yet.
    ``Accepted`` -- agreed it should be fixed, not started.
    ``In progress`` -- being worked on.
    ``Fixed`` -- done; put the commit in ``Resolution``.
    ``Rejected`` -- decided against; put the reasoning in ``Resolution``.
    ``Deferred`` -- real, but not now.

``Severity``
    ``High`` / ``Medium`` / ``Low``. Judged by user-visible impact, not by how
    hard it is to fix.

``Area``
    Roughly which part of the system, so related issues can be read together.

``Reported`` / ``Source``
    When it was found and what found it.

``Evidence``
    The test that pins the current behaviour, where one exists. Every issue
    below that describes a defect has one: the suite asserts what the code does
    *today*, so fixing the issue means deliberately changing a test rather than
    discovering a surprise.

``Decision``
    Left as ``undecided`` until the maintainer rules on it. This is the field to
    fill in when reviewing the list.

``Resolution``
    Commit, or the reason for rejecting.


Open issues
===========

All eighteen came out of the test coverage work on branch
``test-coverage_g78``. None are fixed: each one either changes behaviour that
is visible in production or deletes code, so each wants a decision first.

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 001 High     models / public site    Public species list shows removed species
 002 High     models / admin          Photo auto-attach can break every Photo save
 003 Medium   models / photos         Photo-to-species matching is case-sensitive
 004 Medium   templates / public      Broken placeholder image on every observation page
 005 Medium   templates / public      Search box on the public species list is disabled
 006 Low      templates / cleanup     Dead template: planted-species-compact.html
 007 Low      views / public site     Unknown species id renders empty page, not 404
 008 Medium   urls / third party      Photologue gallery index raises on empty database
 009 Medium   admin                   Create Species Sheets breaks without external id
 010 Medium   views / labels API      Labels API pairs items to labels by position
 011 Medium   templates / operations  Species report opens every image to pick a class
 012 Medium   models / performance    public_planted issues one COUNT per planting
 013 Low      admin / documentation   Stale FIXME comments claim features are broken
 014 Low      templatetags / vendored Dead code in the vendored identifier_for_field
 015 Low      templatetags / frontend bush_shadow mixes integer and float division
 016 Medium   forms / py3 migration   remove_diacritics silently breaks on Python 3
 017 High     tests / gap             Browser suite unrunnable, Vue editor untested
 018 Medium   process                 No CI: the suite is only ever run by hand
==== ======== ======================= ==================================================

Suggested reading order for a first review: 001, 002 and 017 are the ones with
real consequences. 013, 006 and 015 are cheap tidying. 016 and 018 are about
the future rather than today.


Already fixed
=============

Found by the same work and fixed as part of it, each with a regression test.
Listed here so the record is complete; no issue file was opened for them.

============================================= =========
Defect                                        Commit
============================================= =========
Admin Observation form crashed on an empty     b8ad488
database: ``get_next_observation_extid()``
indexed ``[0]`` into an empty queryset, and
NULL ids sort first on PostgreSQL
``Species.nicknames()`` called a manager       b8ad488
method that does not exist; dead and broken,
so removed
``PlantingAdmin.coordinates`` reused ``{0}``   c10a156
and ``{1}``, silently never showing width
and depth
``get_labels_data`` printed to stdout on       da7a076
every request
``media_root`` test fixture did not actually   1e3f7fb
redirect file storage, so uploads leaked
between tests
============================================= =========


Observations, not actionable
============================

Noted while testing; nothing to do, but worth knowing before someone
rediscovers them.

* **The admin login gate does not redirect.** Django 1.5 returns 200 rendering
  the login form at the requested URL rather than 302 to ``admin:login``. No
  data leaks. Later Django versions redirect.
* **``months.month_name`` returns a lazy translation proxy.** ``x in
  month_name(...)`` raises ``TypeError: coercing to Unicode``. Fine in
  templates, a trap for Python callers; force it with ``format()``.
* **``/photologue/`` answers 301**, not 302 -- it is a permanent
  ``RedirectView``.
* **Grappelli skips an empty dashboard module entirely**, so "Recent Actions"
  has no heading until a ``LogEntry`` exists.
* **``PhotoForm`` cannot be instantiated without a database.** Photologue's
  ``post_init`` receiver queries ``PhotoSize``, so even pure form tests need
  ``@pytest.mark.django_db``. ``PhotoSizeCache`` is a Borg whose state outlives
  the test transaction.
* **The repository's Python 3 lint hooks report false positives** on this
  Python 2.7 code -- unresolved imports for ``django``, ``photologue`` and
  ``south``, which only exist inside the dev container. ``ty.toml`` silences
  the import rules for this reason.
