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

None are fixed: each one either changes behaviour that is visible in
production, deletes code, or commits to a piece of work, so each wants a
decision first.

They come from two pieces of work. **001-018** came out of the test coverage
work on branch ``test-coverage_g78``; each has a test pinning the current
behaviour, so fixing one means deliberately changing a test.
**019-036** came out of the dependency and platform upgrade analysis on branch
``requirements-update-plan`` (``docs/upgrade-plan.rst``). Those mostly have no
``Evidence`` entry, because they concern configuration, packaging and future
versions rather than code paths a test can reach.
**037** came out of a later walkthrough of how photo management is meant to be
used, and is about missing documentation rather than a defect, so it has no
``Evidence`` entry either.

From the test coverage work
---------------------------

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

From the dependency upgrade analysis
------------------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 019 High     settings / upgrade      Settings define no MIDDLEWARE
 020 Low      dependencies / cleanup  django-indexer and django-paging are unused
 021 Low      settings / dependencies gunicorn is an app for a removed command
 022 Low      urls / cleanup          Dead /media/grappelli/ route, ADMIN_MEDIA_PREFIX
 023 Medium   settings / upgrade      contrib.messages configured but not installed
 024 Medium   settings / py3          TEMPLATE_DIRS hardcodes a python2.7 path
 025 High     security / settings     SECRET_KEY and DB password are committed
 026 Medium   settings / deployment   ALLOWED_HOSTS is set nowhere in the repository
 027 High     dependencies / build    No upper bounds; --no-deps is load-bearing
 028 Medium   dependencies            photologue <=3.15.1 breaks on Pillow >=10
 029 Low      dependencies / build    gunicorn <=20.1.0 breaks on setuptools >=82
 030 Low      dependencies / build    django-sortedm2m <2 cannot be built by modern tools
 031 Medium   dependencies / build    Three dependencies install from URLs, not PyPI
 032 Low      deployment / cleanup    fabfile.py duplicates the Ansible deployment
 033 Low      dependencies / cleanup  django-pserver is required but never used
 034 High     templatetags / upgrade  admin_list fork needs re-syncing 19 times
 035 Low      dependencies / arch     photologue and grappelli cap the Django version
 036 High     platform / security     The runtime stack is end-of-life and unpatched
==== ======== ======================= ==================================================

**036 is the umbrella** -- the Python 2.7 / Django 1.5 modernisation, planned in
``docs/upgrade-plan.rst``. Read it first; it lists which of the others block it.

Of the rest, 025 and 026 are security questions independent of the upgrade and
can be decided immediately. 019, 023 and 024 are one-line defensive changes that
are no-ops today and prevent silent breakage later -- the cheapest things on this
list. 027 is the one with a real design decision in it. 034 wants deciding before
the upgrade reaches Stage 6. 020, 021, 022, 032 and 033 are deletions.


From the photo management walkthrough
-------------------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 037 Medium   admin / usability       No in-UI instructions for managing plant photos
==== ======== ======================= ==================================================

Read together with 002 and 003, which concern the same auto-attach signal: if
that behaviour changes, the instructions asked for here change with it.


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

From the test coverage work
---------------------------

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

From the dependency upgrade analysis
------------------------------------

Suspected problems that turned out **not** to be problems. Recorded so nobody
spends time re-investigating them.

* **ExifRead is safe across its whole range.** photologue calls exactly one
  function, ``exifread.process_file``, and it is present and unchanged from
  2.1.2 through 3.5.1. The 2.x to 3.x major bump does not affect this project.
* **``Image.FLIP_LEFT_RIGHT`` and ``Image.ROTATE_180`` still work on Pillow
  12.** photologue uses both. Only ``Image.ANTIALIAS`` was removed -- see issue
  028.
* **pytz is safe.** Django 1.11 through 3.2 depend on it without an upper
  bound, but it is a data package with a stable API; a 2026 release works with
  Django 1.11.
* **sqlparse and asgiref are safe.** Django bounds them itself
  (``asgiref<4``, ``sqlparse>=0.3.1``), so they need no attention.
* **``pytest-django==2.9.1`` is good to Django 1.9**, not just 1.5. Its
  ``tox.ini`` lists Django 1.4 through 1.9. The comment in
  ``requirements/testing.txt`` -- "the last release supporting Django 1.5" --
  is true but reads as more limiting than it is: the test stack needs no
  attention for the first seven upgrade stages.
* **``grappelli.dashboard`` survives to grappelli 5.0.0.** It was worth
  checking, since ``ylaneenkasvit/dashboard.py`` depends on it and it is an
  optional sub-application.
* **``uv`` cannot target Python 2.7** (its floor is 3.6), so the early upgrade
  stages cannot be resolved with it and stay hand-maintained. Not a defect in
  anything, but it is the reason ``upgrade-plan.rst`` Appendix A starts at
  Stage 10.
