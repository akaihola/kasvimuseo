======================================================
Issue 020: django-indexer and django-paging are unused
======================================================

:Status: Fixed
:Severity: Low
:Area: dependencies / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none -- ``grep -rn "indexer\|paging" --include='*.py' --include='*.html'`` matched only ``INSTALLED_APPS`` when this was filed, and matches nothing now)
:Depends on: (none)
:Blocks: 036 -- Stage 0
:Related: (none)
:Decision: Remove both, from ``requirements/production.txt`` and from ``INSTALLED_APPS``. No database change is made with them: ``paging`` has nothing in the database, and ``indexer``'s one table stays behind, empty, next to the sentry tables from the same integration.
:Resolution: 0c82b49 -- with issues 021 and 033, which edit the same six lines

Problem
=======

``requirements/production.txt`` pins ``django-indexer==0.3.0`` and
``django-paging==0.2.4``, and ``ylaneenkasvit/common_settings.py`` lists
``indexer`` and ``paging`` in ``INSTALLED_APPS``.

Nothing else in the repository mentions either one -- not a Python import, not
a template tag, not a template. Both are early Sentry dependencies that came
along with a long-removed integration; ``common_settings.py`` still carries the
``# TODO: configure raven`` comment from the same era.

Neither has been released since 2012.

Impact
======

Two abandoned packages installed and initialised on every request path for no
reason. Each is also an obstacle in the upgrade: any package in
``INSTALLED_APPS`` has to keep loading under every future Django version, and
these two will not.

Options
=======

Remove both from ``production.txt`` and from ``INSTALLED_APPS``. Removing an
app that contributes no models and no migrations has no database consequence.

Worth doing before the upgrade starts rather than during it -- see
``docs/upgrade-plan.rst``, Stage 0, which groups this with the other
zero-risk removals.

Decision
========

Done as described: both pins are out of ``requirements/production.txt`` and
both entries are out of ``INSTALLED_APPS``. It went in with issues 021 and 033,
which edit the same tuple and the same two requirements files, and share this
one's verification.

**The sentence above about models and migrations is half wrong**, which is why
it was measured rather than repeated. Read out of the installed packages in the
development image:

=================== ========================== ==============================
Package             ``models.py``              South migrations
=================== ========================== ==============================
``django-paging``   0 bytes                    no ``migrations`` package
``django-indexer``  ``BaseIndex``, ``Index``   ``0001_initial``: creates
                                               ``indexer_index``
=================== ========================== ==============================

So ``paging`` really has no database consequence, and ``indexer`` does have
one: the production dump carries the ``indexer_index`` table, its sequence, and
one ``south_migrationhistory`` row (``indexer / 0001_initial``). The table holds
**zero rows** -- it was written by Sentry's indexing, and Sentry has been gone
since before this dump.

Removing the app leaves the table and the history row in place. That is a
deliberate no-op rather than an oversight:

* nothing is lost, because there is nothing in it;
* nothing reads it, in this repository or in any installed package that remains;
* it is not alone. The same dump still has ``sentry_message``,
  ``sentry_groupedmessage``, ``sentry_filtervalue`` and ``sentry_messageindex``,
  and twelve ``south_migrationhistory`` rows for ``sentry`` -- an app that has
  not been in ``INSTALLED_APPS`` for years. Deleting orphan tables from
  production is one act, to be decided and run once against the real database,
  and it is not a settings change. This issue does not make it.

The one visible effect is that South no longer offers to migrate ``indexer``:
``manage.py migrate`` after the change runs ``kasvimuseo`` and ``photologue``
and nothing else.

The ``# TODO: configure raven`` comment at the end of ``INSTALLED_APPS`` is from
the same era but is left alone -- it is a note about something that might be
wanted, not configuration for something that is not.

Verification
============

Shared with issues 021 and 033; recorded here in full because the
``INSTALLED_APPS`` edits are the risky part of all three.

**The greps are empty.** Re-run after the change, from the repository root::

    $ grep -rn "indexer\|paging" --include='*.py' --include='*.html' \
          --exclude-dir=.dev .
    $ git grep -n "pserver\|indexer\|paging" -- . ':!docs'

Both print nothing and exit 1. Outside ``docs/``, the three names now appear
nowhere in the repository -- not in a settings module, not in an import, not in
a template. The ``--exclude-dir`` is why the first command is written that way
and not as this issue's ``Evidence`` field has it: ``.dev/docs/html/`` is the
untracked Sphinx output, and once the documentation has been built it contains
this page, whose *filename* has both words in it. ``git grep`` does not have
the problem, since the directory is not tracked.

**The image really drops them.** ``dev/Containerfile`` installs from
``requirements/``, so the change was rebuilt rather than only written down --
and rebuilt with ``--no-cache``, from the base image up, which is what CI does
on a fresh runner (issue 018)::

    $ python -c "import indexer"   ->  ImportError: No module named indexer
    $ python -c "import paging"    ->  ImportError: No module named paging
    $ python -c "import pserver"   ->  ImportError: No module named pserver
    $ python -c "import gunicorn"  ->  0.17.4

``pip freeze`` in that image is 21 packages, and the three are in none of them,
while ``gunicorn==0.17.4`` (issue 021 keeps it) and
``django-extensions==1.5.9`` (issue 033 keeps it) are both there. The build's
own guard passed too: the step that fails rather than ship an English admin
(issue 040) found Django's Finnish catalogs where it expects them.

**The suite passes**: ``dev/kasvimuseo app test`` -- 406 passed.
``manage.py validate`` reports 0 errors.

**The site serves.** The production dump was restored, migrated forward, and
the pages were loaded over HTTP from ``dev/kasvimuseo app run`` -- which is
gunicorn, so a short response is an error rather than a silent truncation
(issue 044). All answered ``200`` with their content:

* public: ``/kasvimuseo/planted-species/`` (53,540 bytes),
  ``/kasvimuseo/planted-observation/1291/``,
  ``/kasvimuseo/planting-labels/``, ``/kasvimuseo/planting-labels/data/``
  (54,613 bytes -- the response issue 044 was about),
  ``/kasvimuseo/map/22/``, ``/photologue/gallery/``, ``/accounts/login/``
* the reports: ``/kasvimuseo/planted-species-printable/1,100,102/`` and
  ``/kasvimuseo/planted-species-compact/1,100,102/``
* the admin, logged in as a superuser: ``/admin/``,
  ``/admin/kasvimuseo/species/`` (137,542 bytes),
  ``/admin/kasvimuseo/planting/``, ``/admin/kasvimuseo/observation/``,
  ``/admin/photologue/photo/``, ``/admin/auth/user/``

"Logged in as a superuser" is the part of that worth pinning down, because a
``200`` from the admin does not by itself mean the page rendered: Django 1.5
answers an unauthenticated admin URL by rendering the login form *at the
requested URL* rather than redirecting to it, so a check for ``200`` alone
passes on the login form (``docs/issues/README.rst`` records this under
"Observations, not actionable"). The session here was established by posting
the form with its CSRF token and following the ``302`` back to ``/admin/``, and
the sizes are what distinguish the two: ``/admin/`` is **18,319 bytes** with
that session and **7,088** without it. The change lists are larger still --
``/admin/kasvimuseo/observation/`` is 140,264 -- so those are the real pages.

The same distinction reaches the public pages, which is worth knowing before
comparing two runs of this check: the species list above is 53,540 bytes
fetched anonymously and 53,756 with that session still in the cookie jar. The
whole difference is one element -- ``diff`` shows a single added line, the
log-out link the base template gives a logged-in visitor -- and it carries the
user's name, so the number moves with the length of whatever account did the
check.

Nothing in the server log mentions ``indexer``, ``paging`` or ``gunicorn`` as an
app.

One thing worth writing down for whoever restores that dump next, because it
looks exactly like a regression from a change like this one and is not: the
first pass answered ``500`` on the species list, the observation page and the
species and planting change lists, with ``column
kasvimuseo_species.photo_is_horizontal does not exist``. That column is issue
011's migration; the dump predates it. ``dev/kasvimuseo app manage migrate``
after ``db restore`` is what fixes it, and every page above was then ``200``.
