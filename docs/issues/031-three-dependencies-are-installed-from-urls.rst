=====================================================================
Issue 031: Three dependencies were installed from URLs, not from PyPI
=====================================================================

:Status: Fixed
:Severity: Medium
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: 032 -- **met**: deleting ``fabfile.py`` removed ``flax``, one of
    the three
:Blocks: 036 -- Stage 0
:Related: 032
:Decision: Vendor ``django-jqm`` into the repository, as the Options section
    below and ``docs/upgrade-plan.rst`` Stage 0 both recommend. Asked of the
    maintainer rather than assumed, since the field was ``undecided`` and the
    alternative -- publishing the fork to a package index -- was a real option
    and not this repository's to take; the answer was to vendor it, and to keep
    it a top-level app rather than fold it into ``kasvimuseo``. The evidence
    would have carried the same ruling on its own: nobody else maintains the
    fork, it has no version history to be worth resolving, it is six templates
    and two static files, and the Django-version fixes those templates need
    between here and Stage 19 are edits somebody has to make in *some*
    repository -- vendoring only decides which one, and the one where the
    templates are already overridden is this one.
:Resolution: 9bc7a7c -- the vendored copy in ``jqm/``, the deleted
    requirement line, and the ``setup.py`` and ``Dockerfile`` changes that
    make the production image carry it.

Problem
=======

Three requirements were fetched over the network from places that are not a
package index. All three have now gone, each with the thing that wanted it, and
the annotations below say which; **``django-jqm`` was the one that mattered**,
being the only one of the three in production, and it is the one this issue was
left open for.

``django-jqm`` (``production.txt``) -- **gone**
    ``https://github.com/akaihola/django-jqm/archive/1.1.0.2.zip`` -- a
    personal fork. Every production build depended on that GitHub URL being
    reachable and unchanged. The package is small: seven templates, two static
    files and three near-empty modules. It is vendored into ``jqm/`` in this
    repository now, and the requirement line is deleted; ``jqm/README.rst``
    records the URL, the version and the date it was taken, and says what was
    copied and what was not.

``flax`` (``dev.txt``) -- **gone**
    ``git+https://github.com/akaihola/django-flax@868c863...`` -- pinned to a
    commit, so at least reproducible, but still a personal repository. It was
    used only by ``fabfile.py``, and issue 032 deleted that file and both of
    the lines in ``dev.txt`` that existed for it, ``flax`` and
    ``Fabric==1.6.0``, having established that ``ansible/install.yaml`` and
    ``dev/kasvimuseo`` cover everything it did.

``podman-compose`` (``integration-tests.txt``) -- **gone**
    ``https://github.com/containers/podman-compose/archive/devel.zip`` --
    pinned to a **moving branch**, not a release or a commit, so what it
    installed changed without notice. It was there for the browser suite's
    ``docker-compose.yml``, and issue 017 deleted both the suite and
    ``requirements/integration-tests.txt`` with it.

None had a version history that could be reasoned about, which is why
``docs/dependency-inventory.rst`` had to list them separately from the other 49
packages. The title and the count above are left as they were filed, in the
past tense; the annotations are the corrections rather than a rewrite.

Impact
======

Builds were not reproducible and not offline-capable. A GitHub outage, a
renamed repository or a deleted account broke production deployment, not just
development. ``devel.zip`` in particular meant the integration test environment
could change under the project with no commit to show for it -- which stopped
being true when that environment went (issue 017).

``django-jqm`` was the one that mattered, because it was a production
dependency, and with ``flax`` gone as well it was the last one. ``README.rst``
named this issue as the reason the image build "goes red without anybody
changing anything" -- and that entry, which counted two, was corrected to one,
since ``flax`` was in ``dev.txt`` and ``dev/Containerfile`` installs
``production.txt`` alone. So the image never had more than the one URL that
could fail it, and now it has none: ``README.rst`` says so instead.

Options
=======

``django-jqm``
    **Vendor it into the repository.** It is small, it is a fork nobody else
    maintains, and vendoring turns the Django-version fixes its templates will
    need during the upgrade into ordinary in-repo edits rather than a
    round-trip through another repository. Upgrade plan Stage 0. **Taken.**

``flax``
    Nothing left to do: it went with ``fabfile.py``, since
    ``ansible/install.yaml`` already did the same job. See issue 032, which
    also records what that file was the only copy of.

``podman-compose``
    Nothing left to do: it was development tooling for the browser suite, and
    both went with issue 017.

What was vendored, and what was not
===================================

The package was read before any of it was moved, rather than copied whole: it
is a general-purpose set of jQuery Mobile page templates, and this project uses
part of it.

**Used, and copied.** Six of the seven templates and both static files.
``kasvimuseo/templates/kasvimuseo/reports/planted-species-list.html`` and
``planted-species-base-compact.html`` extend ``jqm/simple.html``, and
``ylaneenkasvit/urls.py`` names ``jqm/login.html`` and ``jqm/logout.html`` as
the templates for ``django.contrib.auth``'s login and logout views. From those
four, ``{% extends %}`` and ``{% include %}`` reach ``jqm/v1_1_0.html``,
``jqm/messages.html`` and ``jqm/formfields.html``. ``v1_1_0.html`` names both
static files, so every page built on any of them asks for
``css/jqm-django.css`` and ``js/jqm-django.js``.

**Left behind.** ``jqm/form.html``, the seventh template: it renders a whole
form page for a generic view, and nothing in this repository extends, includes
or names it, nor passes the ``title``, ``form`` and ``submit`` context it
wants. And the three near-empty modules -- ``models.py`` and ``views.py`` are
``startapp`` stubs containing nothing but their "Create your ... here"
comments, and ``tests.py`` is the scaffolding ``TestCase`` that asserts 1 + 1
is 2. Django 1.5 does not require an installed app to have a ``models`` module,
so ``'jqm'`` stays in ``INSTALLED_APPS`` -- which is what makes the
app-directories template loader and the ``staticfiles`` app-directories finder
look inside the package -- with none of the three present. Upstream's ``doc/``,
``images/``, ``setup.py`` and ``MANIFEST.in`` went too; this repository's
``setup.py`` declares the package data instead.

**Not changed, and worth saying so.** ``v1_1_0.html`` loads jQuery 1.7.2 and
jQuery Mobile 1.1.0 from ``code.jquery.com``. That is a page asset the
visitor's browser fetches, not a build input, so it is outside what this issue
is about: the builds now reach no host but PyPI, and a rendered page still asks
the CDN for its scripts. Bringing those in as well is a separate change with a
different argument.

Verification
============

* ``grep -rn '://' requirements/`` matches nothing. No file under
  ``requirements/`` installs from a URL or a VCS reference any more, which is
  the whole of what this issue asked for.

  One thing that grep deliberately does not cover, so that nobody rediscovers
  it as an unfinished part of this: ``ansible/install.yaml`` still installs
  **pip itself** from ``https://github.com/rouge8/pip/archive/gh-5780.zip``,
  and installs the application from ``git+ssh://`` at bitbucket. Neither is a
  requirement of the application -- the first is the deployment host's own
  tooling, patched for a pip bug, and the second is how the code gets to the
  server at all. They belong to the deployment, not to the dependency set this
  issue is about, and the upgrade plan reaches the first of them at Stage 10,
  where the interpreter that needs that pip is replaced.
* ``dev/kasvimuseo app test``: 426 passed. The development image was rebuilt
  first, so ``django-jqm`` is not installed in it -- ``pip freeze`` does not
  name it -- and the login, logout and report pages the suite renders come from
  the vendored copy on ``PYTHONPATH``.
* ``dev/kasvimuseo app browser-test``: 25 passed.
* ``podman build -f Dockerfile .`` succeeded, and the resulting image was
  inspected rather than trusted: all six templates, both static files and the
  README are under ``site-packages/jqm/``, ``find_template`` resolves each of
  the six and raises ``TemplateDoesNotExist`` for ``jqm/form.html``, and
  ``staticfiles``' finders locate both assets in the package. The only hosts
  the build contacts are PyPI and the Alpine package mirror the base image
  already used for its C libraries.
* ``dev/kasvimuseo docs --clean`` builds with no warnings.
