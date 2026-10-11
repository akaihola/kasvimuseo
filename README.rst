Kasvimuseo
==========

This guide helps developers run and test the plant catalogue locally.
Private deployment configuration and operations records live in the separate ``kasvimuseo-deployment`` repository.

License
-------

The project uses the BSD 3-Clause license, identified by SPDX as ``BSD-3-Clause``.
Read `LICENSE <https://github.com/akaihola/kasvimuseo/blob/main/LICENSE>`_ for the copyright notice and terms.
Read `Third-party notices <https://akaihola.github.io/kasvimuseo/third-party-notices.html>`_ for vendored component licenses.

Development setup
-----------------

Install Podman, PostgreSQL command-line tools, and uv.
Run these commands from the checkout::

    dev/kasvimuseo app build
    dev/kasvimuseo db bootstrap
    dev/kasvimuseo app manage createsuperuser
    dev/kasvimuseo app run

Open http://localhost:8000/.
The development database and generated documentation live under ``.dev/``.
The application stores uploaded photos under ``media/``.
``.gitignore`` keeps ``.dev``, ``.claude/``, and the machine-specific settings
modules out of Git. ``.containerignore`` keeps them out of the Podman build
context. ``kasvimuseo/tests/test_ignore_rules.py`` checks both files with the
committed rules alone (task 4).

Use ``dev/kasvimuseo app run --runserver`` for automatic Python reloads.
Use ``dev/kasvimuseo app manage <command>`` for Django management commands.
The helper starts PostgreSQL when needed and stops it when the command exits.

Restore a database supplied by its owner::

    dev/kasvimuseo db restore /path/to/backup.sql

Use ``db development <input.sql> <output.sql>`` to create a copy with development passwords.
Keep database backups and uploaded media outside Git.
The private repository owns remote backup commands.

Local media
-----------

The development server serves local files under ``/media/``.
Missing files return HTTP 404 by default.
Set ``KASVIMUSEO_MEDIA_FALLBACK_URL`` to an authorized media source when you need a fallback.
The ``media fetch`` command downloads images referenced by the local database::

    KASVIMUSEO_MEDIA_FALLBACK_URL=https://media.example.invalid/ dev/kasvimuseo media fetch

Development login
-----------------

The development helper enables ``/dev-login/<username>/`` for existing active users.
This route grants access without a password to anyone who can reach the development server.
Set ``KASVIMUSEO_DEV_LOGIN=`` to disable it::

    KASVIMUSEO_DEV_LOGIN= dev/kasvimuseo app run

Site configuration
------------------

``ylaneenkasvit.ylaneenkasvit_settings`` reads these required environment variables:

* ``KASVIMUSEO_DB_NAME`` and ``KASVIMUSEO_DB_USER`` select the database and its account.
* ``KASVIMUSEO_DB_PASSWORD`` supplies the database password.
* ``KASVIMUSEO_SECRET_KEY`` supplies the Django signing key.
* ``KASVIMUSEO_ALLOWED_HOSTS`` supplies a comma-separated list of accepted host names.

Optional variables configure installation-specific values:

* ``KASVIMUSEO_SITE_ROOT`` selects the directory containing static files and media.
* ``KASVIMUSEO_DB_HOST`` and ``KASVIMUSEO_DB_PORT`` select the database connection.
* ``KASVIMUSEO_STATIC_URL`` and ``KASVIMUSEO_MEDIA_URL`` select public asset paths.
* ``KASVIMUSEO_SITE_TITLE`` selects the administration title.
* ``KASVIMUSEO_ADMIN_EMAIL`` and ``KASVIMUSEO_ADMIN_NAME`` select the error-report recipient.

The development helper and test settings supply their own local values.
Private inventories, site settings, account records, and deployment instructions belong in ``kasvimuseo-deployment``.

Embedding the species list
--------------------------

Embedding page authors can use this script to show the species list from the catalogue::

    <script src="https://static.plants.example.invalid/js/kasvimuseo/planted-species-iframe.js"></script>

The loader reads its own address from ``document.currentScript.src``.
The origin is the scheme, hostname, and port of that address.
The loader removes one leading ``static.`` hostname label and keeps the scheme and port.
The example requests ``https://plants.example.invalid/kasvimuseo/planted-species/``.
Without that label, the loader uses the script's origin unchanged.
This also works when the embedding page uses a third origin, such as ``https://museum.example.invalid``.
The embedding page needs no configuration attribute.
Deployments that need another address rule must configure it in the deployment repository.

Testing
=======

Two suites, on two interpreters, and the split is deliberate (issue 017)::

    $ dev/kasvimuseo app test                 # the application
    $ dev/kasvimuseo app browser-test         # the label editor, in two browsers

``app test`` is the one you want almost always: pytest inside the Python 2.7
container, about twenty seconds, its own PostgreSQL, no dump and no media.

``app browser-test`` runs ``browser_tests/`` on the **host's** Python 3, through
uv, driving Playwright against the real application in its own
container. It covers what only exists in a browser: dragging museum numbers
between labels, the save cycle, the per-label photo and the print toggle --
and, since issue 013, the two admin changelist controls Grappelli builds out of
JavaScript, its filter pulldown and its action dropdown. The
application is Python 2.7 and nothing that drives a current browser supports
2.7, which is why this half lives outside the container -- and Playwright can
drive WebKit, which is the engine the iPad work (issue 045) needs and no
browser old enough for 2.7 could have provided.

**Every test runs in both engines** since issue 061: Chromium, and Playwright's
WebKit, which is what iOS Safari is built on and the engine every defect this
page has been reported for came from. A test is named after the engine it ran
in -- ``test_a_tap_on_a_number_moves_nothing[webkit]`` -- and either engine can
be run on its own::

    $ dev/kasvimuseo app browser-test --engine webkit
    $ KASVIMUSEO_BROWSER_ENGINES=chromium dev/kasvimuseo app browser-test

WebKit skips the six touch-drag tests. They dispatch the gesture over the
Chrome DevTools Protocol so the browser does its own hit-testing, and WebKit
speaks no CDP; the skip names that reason where it happens. It is not Safari
either: it is Safari's engine on Linux, without iOS, so an ``@supports
(-webkit-touch-callout: none)`` rule is as false there as in Chromium (issue
056). What it does share is how text is measured, which is what the iPad
reports have all been about.

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
if you have them already, or install them once::

    $ uv run --no-project --with-requirements browser_tests/requirements.txt \
          playwright install chromium webkit

The page loads Vue, axios and sanitize.css from CDNs; the tests answer those
requests from ``browser_tests/vendor/`` instead, so a run needs no network.
``docs/third-party-notices.rst`` records the version and the license of each
copy.


Continuous integration
======================

The suite runs on GitHub Actions, from
``.github/workflows/tests.yml`` (issue 018), on every pull request and on every
push to ``main``. Those two triggers rather than a bare ``push:``: a branch
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

A full run is about a minute and a half on a hosted runner, the four jobs in
parallel: ``pytest`` builds the Python 2.7 image from scratch and runs the suite
(68 s), ``sphinx`` builds the documentation with ``--clean`` (25 s) -- which is
how a malformed issue field is caught on push rather than by whoever next builds
the docs -- and
``playwright`` runs the browser tests (97 s), the slowest of the three because
it needs both the image and a browser. That last one is a separate job rather
than a step in ``pytest`` so that a drag-and-drop regression and a model
regression arrive as two different red lights; the price is that both jobs build
the same image.

Since issue 061 ``playwright`` is a matrix of two, ``playwright (chromium)`` and
``playwright (webkit)``, for the same reason: an engine regression should say
which engine, and WebKit is the engine every defect on the label page has been
reported from. They run in parallel, so the wall clock of a run is unchanged and
the price is again one more image build. WebKit's leg is green with six
touch-drag tests skipped; the reason is in ``browser_tests/conftest.py``.

A fourth job, ``pages``, runs only on a push to ``main`` and publishes what
``sphinx`` built. A pull request builds the documentation and fails on a warning
like any other check, and deploys nothing.

**GitHub is the only remote**, ``origin``. The maintainer dropped the Bitbucket
mirror on 2026-10-09. CI tests a change only after it reaches GitHub::

    $ git push origin main

Until then, only the commands that you run test it. The hook below runs the
suite for you before each push.

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
* **playwright** -- run ``dev/kasvimuseo app browser-test --engine <the one the
  red job names>`` here, or leave the flag off and get both. Same image and
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


Before a release
----------------

This section is for the package maintainer who builds a source distribution or
a wheel. Build from a clean checkout, then run the artifact check::

    $ python3 setup.py sdist bdist_wheel
    $ python3 dev/check-release-artifacts dist/*.tar.gz dist/*.whl

The check fails on a machine-specific settings module, on a marker value you
pass with ``--marker``, and on a missing template, catalog, static file,
migration or third-party license notice. ``docs/third-party-notices.rst``
lists every copied component with its license and notice file (task 7).
``setup.py`` names the private modules in ``PRIVATE_MODULES`` and drops them
from every build; ``kasvimuseo/tests/test_release_artifacts.py``
proves it with a planted ``local_settings.py`` behind a symlink (task 1). The
production image runs the same check on the installed package.


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

The docs as they stand on ``main`` are at

    https://akaihola.github.io/kasvimuseo/

published by the ``pages`` job of ``.github/workflows/tests.yml`` on every push
to ``main``, from the same ``dev/kasvimuseo docs --clean`` build the ``sphinx``
job runs. Nothing else publishes: a pull request builds the documentation and
fails on a warning, but deploys nothing, so the site is always what has landed.

**One manual step, once.** A workflow cannot switch GitHub Pages on for its own
repository, so somebody with access has to set **Settings -> Pages -> Source**
to *GitHub Actions*. Until that is done the ``pages`` job notices there is no
Pages site, skips the deployment with a notice and leaves the run green, and the
address above does not answer; afterwards the next push to ``main`` publishes
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
