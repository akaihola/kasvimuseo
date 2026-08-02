Development setup
=================

The app is Django 1.5 on Python 2.7, which no longer exists in current
distributions, so it runs in a container. The database runs natively as a
throwaway PostgreSQL cluster inside the working copy. Everything is driven by
one script, ``dev/kasvimuseo``; all its state lives under ``.dev/`` and can be
deleted at any time.

Requirements: ``podman`` and a PostgreSQL client/server installation (any
version from 9.x up; 15 is known to work).

Build the app image once::

    $ dev/kasvimuseo app build

Copy the production database and load it locally::

    $ dev/kasvimuseo db fetch                        # -> .dev/backups/production.sql
    $ dev/kasvimuseo db restore .dev/backups/production.sql

``db fetch`` runs ``pg_dump`` over SSH. It needs an account on
``kasvit.ambitone.com`` whose key is authorised; override the default with
``KASVIMUSEO_PROD_SSH=user@host``. Without SSH access, produce the dump with
Ansible instead and restore that file::

    $ ansible-playbook -t backup -e backup_database=/backup-dir ansible/install.yaml
    $ dev/kasvimuseo db restore /backup-dir/vps763955.ovh.net/tmp/backup.sql

To work without any production data, build an empty database from the
migrations instead, and give yourself an admin account::

    $ dev/kasvimuseo db bootstrap
    $ dev/kasvimuseo app manage createsuperuser

Run the site at http://localhost:8000/ ::

    $ dev/kasvimuseo app run

That serves through **gunicorn**, the WSGI server ``requirements/production.txt``
pins, rather than through ``manage.py runserver``. ``runserver`` is ``wsgiref``:
single-threaded, documented as unfit for anything but local use, and -- the part
that mattered -- it answers HTTP/1.0 with no ``Content-Length``, so the end of
the response is whatever arrived before the connection closed. A page cut short
on the way to the browser then looks complete to the browser and to ``curl``
alike; that is issue 044, where a change form lost its save buttons because the
last 10 KB never arrived and nothing anywhere said so. gunicorn frames its
responses (chunked, HTTP/1.1), so the same cut is reported instead of rendered.

``runserver`` is still there, and is the right choice when you are editing
Python over a loopback-only session::

    $ dev/kasvimuseo app run --runserver

The difference in practice is the autoreloader: ``runserver`` restarts itself
when a module changes and gunicorn 0.17.4 has no ``--reload``. Under gunicorn,
templates and static files are still re-read per request; changed Python needs
either a restart of ``app run`` or a reload of the workers in place::

    $ podman kill --signal HUP $(podman ps -qf name=kasvimuseo-dev-)

The container shares the host's network namespace instead of publishing a port,
which is the other half of issue 044. Rootless podman publishes a port with
pasta, and pasta -- over a connection with real latency -- forwards about 43 KB
of a response and then closes it, losing the rest. Sharing the namespace takes
that layer out: gunicorn listens on the host's port itself. To watch the old
behaviour, or if host networking is unwanted::

    $ dev/kasvimuseo app run --publish

An SSH tunnel also avoids it, by making the remote request a loopback one on
this side, and is the right answer for a ``--runserver`` session::

    $ ssh -N -L 8000:127.0.0.1:8000 <this host>

``/static/`` is served by the app itself in both cases, and only while ``DEBUG``
is on: ``runserver`` does it by magic, and ``ylaneenkasvit/urls.py`` wires the
same staticfiles view up explicitly for every other server. Production serves
``/static/`` from its web server and is unaffected.

Other commands::

    $ dev/kasvimuseo app run --runserver      # the old wsgiref server instead
    $ dev/kasvimuseo app run --publish        # a published port instead of the host's
    $ dev/kasvimuseo db start|stop|status     # PostgreSQL by hand
    $ dev/kasvimuseo db psql                  # psql on the local database
    $ dev/kasvimuseo media fetch              # photos the database references
    $ dev/kasvimuseo db reset                 # delete the cluster entirely
    $ dev/kasvimuseo app manage <args>        # any manage.py command
    $ dev/kasvimuseo app test                 # unit tests; needs no database
    $ dev/kasvimuseo app browser-test         # the label editor, in a browser
    $ dev/kasvimuseo app shell                # shell in the Python 2.7 container

``app run`` and ``app manage`` start PostgreSQL if it is down and stop it again
when they exit, so the cluster only runs while it is needed. Started by hand
with ``db start``, it keeps running until ``db stop``.

Production still runs PostgreSQL 10, so ``db restore`` adapts the dump to a
current server: it drops the PostGIS extension when PostGIS is not installed
locally (no table uses a spatial type) and the one index over ``abstime``, a
type removed in PostgreSQL 12. Both are reported as they are skipped.

Local settings live in ``ylaneenkasvit/local_settings.py``. It is untracked, so
``dev/kasvimuseo`` copies it from ``local_settings.development.py`` the first
time it runs the app; edit your copy freely. Without it the app falls back to
production's static URL and ignores the database environment variables. A copy
made earlier is never overwritten, so when the template gains a setting, add it
by hand -- ``dev/kasvimuseo`` says so for the newest one, ``MEDIA_FALLBACK_URL``.

Secrets come from the environment and are in no tracked file (issue 025). The
site settings read ``KASVIMUSEO_SECRET_KEY`` and ``KASVIMUSEO_DB_PASSWORD`` and
raise ``ImproperlyConfigured`` naming the variable if either is unset -- there
is no default, because a default would silently sign cookies with a value that
is in the git history. ``dev/kasvimuseo`` passes development values for both
into the container, so nothing needs setting to work locally; the test settings
supply their own. In production the two live in the Ansible Vault file
``ansible/host_vars/<host>`` as ``kasvimuseo_secret_key`` and
``kasvimuseo_db_password``, and ``ansible/install.yaml`` writes them into
``uwsgi.ini`` and refuses to run without them. The one thing that needs the
real database password is ``db fetch``, which talks to production::

    $ KASVIMUSEO_DB_PASSWORD=... dev/kasvimuseo db fetch

``ALLOWED_HOSTS`` arrives the same way and refuses to start the same way, from
``KASVIMUSEO_ALLOWED_HOSTS`` -- a comma-separated list of host names (issue
026). It is not a secret, so production's list is tracked, in
``ansible/vars/main.yml`` as ``kasvimuseo_allowed_hosts``, and ``uwsgi.ini``
writes it into the process environment beside the two secrets.
``dev/kasvimuseo`` passes ``*`` into the container, since a development server
is reached under whatever name it was published under, and the test settings
name their own hosts -- so, again, nothing needs setting to work locally. There
is deliberately no default: an empty list makes Django refuse every request and
``['*']`` switches the ``Host`` header check off, so either fallback would
answer a misconfigured deployment silently.

Photos are served by this server, under ``/media/``, and the ones this machine
does not have are redirected to ``media.kasvit.ambitone.com``. So a fresh clone
shows every photo the database references without downloading anything, and a
photo uploaded here is served from here rather than 404ing on a host that never
saw it. The printable and compact species views no longer need the actual files
-- they used to open every one to decide a header class, and raised ``IOError``
when one was missing (issue 011); the orientation is measured once on save and
stored, so browsing the reports against a fresh dump and no local media now
works. Downloading them is worth it anyway if you want to *see* the photos
rather than the redirect, and if you are going to run the migrations over a dump
taken before this change: ``0021_backfill_species_photo_is_horizontal``
measures whatever is on disk when it runs, and leaves the rest portrait until
it is run again with the files there. No SSH needed, the media host is
public::

    $ dev/kasvimuseo media fetch

That is 137 files and about 260 MB at the time of writing, and it skips what is
already there, so it is safe to re-run after restoring a newer dump. The whole
directory, including material no row points at, still needs SSH::

    $ rsync -a akaihola@kasvit.ambitone.com:/www/ylaneenkasvit/media/ media/



Testing
=======

Two suites, on two interpreters, and the split is deliberate (issue 017)::

    $ dev/kasvimuseo app test                 # the application
    $ dev/kasvimuseo app browser-test         # the label editor, in a browser

``app test`` is the one you want almost always: pytest inside the Python 2.7
container, about twenty seconds, its own PostgreSQL, no dump and no media.

``app browser-test`` runs ``browser_tests/`` on the **host's** Python 3, through
uv, driving Playwright's Chromium against the real application in its own
container. It covers what only exists in a browser: dragging museum numbers
between labels, the save cycle, the per-label photo and the print toggle --
and, since issue 013, the two admin changelist controls Grappelli builds out of
JavaScript, its filter pulldown and its action dropdown. The
application is Python 2.7 and nothing that drives a current browser supports
2.7, which is why this half lives outside the container -- and Playwright can
drive WebKit, which is the engine the iPad work (issue 045) needs and no
browser old enough for 2.7 could have provided.

It builds and drops its own database, ``ylaneenkasvit_browsertest``, seeded from
``browser_tests/seed.py``, serves it with gunicorn on the first free port from
8123, and points ``MEDIA_ROOT`` at ``.dev/browser-test-media``. Your database,
your ``media/`` and your ``local_settings.py`` are not read or written.

The editor is staff-only (issue 052), so the seed makes one account for the
tests to log in with and the script generates its password per run, passing it
to both halves in ``KASVIMUSEO_BROWSER_TEST_PASSWORD``. No password is written
down anywhere in this repository -- see issue 050 for why that rule exists. Any
pytest arguments pass straight through::

    $ dev/kasvimuseo app browser-test -k drag -x

The browsers are never downloaded by the script. Set ``PLAYWRIGHT_BROWSERS_PATH``
if you have them already, or install one once::

    $ uv run --no-project --with-requirements browser_tests/requirements.txt \
          playwright install chromium

The page loads Vue, axios and sanitize.css from CDNs; the tests answer those
requests from ``browser_tests/vendor/`` instead, so a run needs no network.


Continuous integration
======================

The suite runs on GitHub Actions, from
``.github/workflows/tests.yml`` (issue 018), on every pull request and on every
push to ``master``. Those two triggers rather than a bare ``push:``: a branch
with a pull request open matches both events, and would run everything twice.
A branch pushed with no pull request open therefore runs nothing, which is what
the hook below is for. The workflow is deliberately thin:
it calls ``dev/kasvimuseo app build`` and ``dev/kasvimuseo app test``, the two
commands above, so what CI runs cannot drift from what you run. It adds only
what a hosted runner does not give the script for free -- Ubuntu keeps
``initdb`` and ``pg_ctl`` off ``PATH``, and a non-login shell leaves ``$USER``
unset.

There is no PostgreSQL *service container*, which is the usual CI shape,
because ``common_settings.py`` names the database host as
``/var/run/postgresql`` -- a unix socket directory, not something reachable
over TCP. The script's throwaway cluster, whose socket directory it
bind-mounts into the container, is the arrangement the settings already
describe. No production dump and no ``media fetch`` are involved: the tests
build their own data, and the test settings point ``MEDIA_ROOT`` at a
throwaway directory, so nothing reads a photo.

A full run is about a minute and a half on a hosted runner, the three jobs in
parallel: ``pytest`` builds the Python 2.7 image from scratch and runs the suite
(68 s), ``sphinx`` builds the documentation with ``--clean`` (25 s) -- which is
how a malformed issue field is caught on push rather than by whoever next builds
the docs -- and
``playwright`` runs the browser tests (97 s), the slowest of the three because
it needs both the image and a browser. That last one is a separate job rather
than a step in ``pytest`` so that a drag-and-drop regression and a model
regression arrive as two different red lights; the price is that both jobs build
the same image.

A fourth job, ``pages``, runs only on a push to ``master`` and publishes what
``sphinx`` built. A pull request builds the documentation and fails on a warning
like any other check, and deploys nothing.

**The workflow only sees the GitHub remote**, ``origin``, which has been the
mirror rather than the one ``master`` tracks. Work that is only ever pushed to
``bitbucket`` is not tested by anything except the hook below::

    $ git push origin master

When a run goes red
-------------------

Both jobs reproduce here, and both fail for the same reasons they would fail
locally:

* **pytest** -- run ``dev/kasvimuseo app test`` in this checkout. Same image,
  same settings; the one thing CI has that you do not is whatever PostgreSQL
  version the runner ships, so a failure that will not reproduce is worth
  reading as a version difference before anything else.
* **sphinx** -- run ``dev/kasvimuseo docs --clean`` and read the ``WARNING``
  lines. ``--clean`` matters: an incremental build cannot report a problem in a
  file nobody touched, and CI always builds from scratch.
* **playwright** -- run ``dev/kasvimuseo app browser-test`` here. Same image and
  same seed data; the runner differs only in where its browser comes from, since
  CI downloads one and you have one already.
* **the image build** -- both jobs above start with ``dev/kasvimuseo app
  build``, and it no longer reaches anywhere but PyPI. One dependency,
  ``django-jqm``, used to install from a personal GitHub URL, which made this
  the one thing here that could go red without anybody changing anything, on
  the day that URL stopped answering. Issue 031 vendored it into ``jqm/``, so
  nothing under ``requirements/`` names a URL and that failure is gone.

Before the push
---------------

``dev/pre-push`` runs the same suite locally before anything leaves the
machine. ``.git/hooks`` is not tracked, so install it once per clone::

    $ ln -sf "$PWD/dev/pre-push" "$(git rev-parse --git-path hooks)/pre-push"

It skips a push that only deletes branches, and ``git push --no-verify`` skips
it entirely. It runs ``app test`` only: the browser suite needs about half a
minute more and a browser, which is more than a push should wait for, so it is
left to CI and to whoever is changing that page.


Documentation
=============

``docs/`` is a Sphinx project: this file, the issue register, the plans, and an
API reference generated from the source. Build it into ``.dev/docs/html/``::

    $ dev/kasvimuseo docs --open

The build treats warnings as errors, so a malformed page or a document nothing
links to makes it exit non-zero -- while still writing the HTML, so the docs
stay current either way. It also generates ``docs/issues/next.rst``, the queue
of what is ready to work on, from the issue files' own metadata, and fails on a
field or a ranking that does not add up; see ``docs/issues/README.rst``. Two reasons to use ``--clean``: an incremental build
re-reads only what changed, so it cannot report a problem in a file nobody
touched, and Sphinx never deletes a page whose source has gone::

    $ dev/kasvimuseo docs --clean

It runs on the host's Python 3 through ``uv``, not in the app container, and
never imports the application -- see
``docs/issues/038-no-rendered-documentation.rst`` for why, and for how it should
change as the stack is upgraded. The toolchain is pinned in
``docs/requirements.txt``; nothing needs installing beforehand.

To rebuild automatically whenever a coding agent edits documentation or Python
source, register the hook in ``.claude/settings.json``. Agents cannot write that
file -- the harness masks it -- so this one is by hand::

    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Write|Edit|MultiEdit",
            "hooks": [
              {"type": "command", "command": "dev/docs-hook", "async": true}
            ]
          }
        ]
      }
    }

``async`` is the part that matters: the hook runs in the background and the
agent carries on. ``dev/docs-hook`` exits immediately for an edit that touches
nothing the documentation is built from, and a rebuild after one that does takes
about six seconds. It stays silent when the build succeeds and reports the file
and line when it does not, so a page broken by an edit is not discovered a week
later.

Reading the published documentation
-----------------------------------

The docs as they stand on ``master`` are at

    https://akaihola.github.io/kasvimuseo/

published by the ``pages`` job of ``.github/workflows/tests.yml`` on every push
to ``master``, from the same ``dev/kasvimuseo docs --clean`` build the ``sphinx``
job runs. Nothing else publishes: a pull request builds the documentation and
fails on a warning, but deploys nothing, so the site is always what has landed.

**One manual step, once.** A workflow cannot switch GitHub Pages on for its own
repository, so somebody with access has to set **Settings -> Pages -> Source**
to *GitHub Actions*. Until that is done the ``pages`` job notices there is no
Pages site, skips the deployment with a notice and leaves the run green, and the
address above does not answer; afterwards the next push to ``master`` publishes
with no change to the workflow. This is the same class of step as registering the
hook above, and for the same reason -- see the "Not done here" section of
``docs/issues/038-no-rendered-documentation.rst``.

Reading the docs from another machine
-------------------------------------

::

    $ dev/kasvimuseo docs serve

Serves every checkout of the repository at once -- the main one and each
worktree, each from its own ``.dev/docs/html/`` -- on port 8800, bound to this
machine's Tailscale address, so it is reachable from the tailnet and from
nowhere else. ``/`` lists the checkouts; each is at ``/<branch>/``, the main
checkout also at the fixed ``/main/`` because its branch changes. Every page
gets a switcher in the corner that jumps to the same page in another checkout.

The list is re-read per request, so worktrees added or removed while it runs
need no restart. It serves what has been built and nothing else: a checkout
whose docs are missing says so, and building it is ``dev/kasvimuseo docs``
*in that checkout*. Stdlib Python 3 only -- ``--port`` and ``--bind`` override
the defaults.


Using Ansible for deployment, update and maintenance
====================================================

Before running ``ansible-playbook``, get the vault password from your password manager
and run::

    export ANSIBLE_VAULT_PASS=***********


Deployment
==========

    ansible-playbook ansible/bootstrap.yml
    ansible-playbook ansible/install.yml

Restoring the database on the server
------------------------------------

    ansible-playbook \
      -t restore \
      -e database_backup_to_restore=local/path/to/backup.sql \
      ansible/install.yaml

Updating the software
---------------------

    ansible-playbook -t code ansible/install.yaml


Maintenance
===========

Backing up the database
------------------------

    ansible-playbook \
      -t backup \
      -e backup_database=/backup-dir \
      ansible/install.yaml

Restoring the database in a development environment
---------------------------------------------------

    sudo -u postgres createdb -O ylaneenkasvit ylaneenkasvit
    sudo -u postgres psql -f /backup-dir/vps763955.ovh.net/tmp/backup.sql ylaneenkasvit

Updating code on the server
---------------------------

    ansible-playbook -t code ansible/install.yaml


The security maintenance window
===============================

Three High-severity issues in ``docs/issues/`` -- 049's rotated ``SECRET_KEY``
and database password, 050's published admin password, and 051's untracked
``local_settings.py`` that forces ``DEBUG = True`` -- are each half done. The repository half of all three has landed; what is left is one act on
the running server, and the three acts are one sequence whose order matters.
That sequence is ``ansible/secure-production.yaml``. This is its runbook.

One command::

    export ANSIBLE_VAULT_PASS=***********
    ansible-playbook ansible/secure-production.yaml

Before running it
-----------------

* **Agree the time with the customer.** The cost lands on them, and issue 049's
  ``Decision`` field says the timing is theirs. Everything under "What the
  customer sees" below happens whenever this is run.
* **Three variables have to be in the vault**
  (``ansible-vault edit ansible/host_vars/vps763955.ovh.net``):
  ``kasvimuseo_secret_key``, ``kasvimuseo_db_password`` and
  ``kasvimuseo_admin_passwords``. The first two are the values the maintainer
  has already rotated; the third is new, and is a mapping of user name to new
  password::

      kasvimuseo_admin_passwords:
        akaihola: ...

  It must name ``akaihola``, the account whose password this repository
  published. Any other account named there is rotated with it; every privileged
  account *not* named there is listed by the play's audit step, so the four
  other accounts issue 050 asks about are visible either way. The playbook stops
  before touching anything if any of the three is missing.
* Nothing else. Do not put any of those values in a tracked file, a commit
  message or a ticket: naming the commit that deployed them is what the issues'
  ``Resolution`` field is for.

What it does, in order
----------------------

#. ``ansible/install.yaml``, imported whole -- the ordinary deploy. It installs
   the current code, sets the PostgreSQL password from the vault, writes
   ``SECRET_KEY``, the database password and ``ALLOWED_HOSTS`` into
   ``/home/kasvimuseo/uwsgi.ini`` and restarts uWSGI. That is issue 049 in its
   entirety, and it is also the step 051 has to happen after. The two values
   land together, which is why the whole playbook is the unit rather than
   ``-t database`` or ``-t web`` on their own.
#. The admin passwords, from the vault (050).
#. A report of every account in ``auth_user`` and what the admin log says it
   did (050 again -- see "What it leaves for you" below).
#. The untracked ``local_settings.py`` and any ``.pyc`` beside it, deleted, and
   uWSGI restarted so the deletion takes effect (051). This step refuses to run
   unless it can see, on the server, that ``ALLOWED_HOSTS`` is already in
   ``uwsgi.ini`` and that the installed settings read the environment. Deleting
   the file before that turns every request into a 400, which is the one
   ordering mistake this playbook exists to make unreachable.
#. Verification, as a play of its own -- see below.

What the customer sees
----------------------

The site is down for as long as one uWSGI restart takes, twice: once when the
deploy rewrites ``uwsgi.ini``, once after ``local_settings.py`` goes. Seconds
each, back to back, so plan for a minute rather than an hour and do it outside
the garden's working day.

Then, and these are consequences of a new ``SECRET_KEY``, not signs of a
problem:

* everybody who is logged in is logged out once, and logs back in normally;
* password-reset links issued before the run stop working -- requesting a new
  one works;
* whoever uses the ``akaihola`` admin account needs the new password.

What to check afterwards
------------------------

The playbook checks, and says so rather than leaving it to be checked by hand.
The last play asserts, on the server:

* ``uwsgi.ini`` carries the three values the vault holds -- printed as three
  booleans, never as the values;
* uWSGI *started after* that file was written, which is the only thing that
  distinguishes a running process signing with the new key from one still
  signing with the old one;
* no ``local_settings.py`` and no ``local_settings.pyc`` is left in the
  installed package (on Python 2 a leftover ``.pyc`` is imported even with no
  ``.py`` beside it, and would turn ``DEBUG`` straight back on);
* an ordinary page still answers 200;
* a request with a host name the site does not answer to gets a 400, and one
  that is not Django's debug page;
* every account named in the vault has the vaulted password. A Django hash
  verifies exactly one plaintext, so that is also the statement that the
  password published in this repository no longer signs anybody in.

It is a separate play so it can be run on its own, later, without changing
anything::

    ansible-playbook ansible/secure-production.yaml -t verify

Running it twice
----------------

Safe. An account that already has the vaulted password is left alone, the
deleted file is already gone, and uWSGI is restarted only if something actually
changed -- so a second run reports no change and does not interrupt the site.
The one exception is ``collectstatic``, which reports itself changed on every
run of ``install.yaml`` and always has.

If it stops half way
--------------------

Every step is safe to re-run, so the answer is almost always to fix what it
named and run the same command again. Two failures have a specific meaning:

* *"The deploy this step depends on has not landed"* -- the ``uwsgi`` tag has
  not run, or the installed code predates issues 025 and 026. Nothing has been
  deleted. Run the whole playbook rather than ``-t localsettings``.
* *the database refuses the password from the vault* -- PostgreSQL still has
  the old one, so the deploy has not run either. Same answer.

What it leaves for you
----------------------

Three decisions the playbook deliberately does not make:

* **when to run it** -- 049's, and the customer's;
* **the other accounts** -- it rotates exactly the accounts the vault names,
  and lists the privileged ones it does not, with their hash algorithm, their
  last login and their admin activity. Choosing new passwords for them, or
  deactivating them, is a judgement about who still needs an account;
* **whether to treat the disclosure as exploited** -- the audit step prints the
  ``LogEntry`` history because it is the only record there is, but reading it
  is a person's job.

Try it without running it
-------------------------

``--check`` is honest here: the password step reports what it *would* set
without writing, the deletion reports the files it would remove without
removing them, and the read-only checks run for real::

    ansible-playbook ansible/secure-production.yaml --check
