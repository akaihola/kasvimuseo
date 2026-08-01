==========================
 django-jqm, vendored here
==========================

The jQuery Mobile page templates the two public reports and the login and
logout pages are built on. This is a copy, not a dependency.

:Upstream: ``https://github.com/akaihola/django-jqm`` -- a personal fork of
    Mike C. Fletcher's ``django-jqm`` (MIT), whose own home was
    ``https://launchpad.net/django-jqm``.
:Version: ``1.1.0.2``
:Taken from: ``https://github.com/akaihola/django-jqm/archive/1.1.0.2.zip``
:Copied on: 2026-08-01, by the change that fixed issue 031.

Why it is here
==============

It used to be a line in ``requirements/production.txt`` pointing at that zip,
so every production build and every container image build depended on one
GitHub URL staying reachable and unchanged -- with no version history behind it
to reason about, because nothing was ever published to a package index. That
was issue 031, and ``README.rst`` named it as the reason the image build could
go red without anybody changing anything.

Nobody else maintains the fork, so there was nothing to lose by copying it and
one thing to gain besides the build: the Django-version fixes these templates
will need on the way up from 1.5 are now ordinary edits in this repository
rather than a round trip through another one. ``docs/upgrade-plan.rst`` has it
as Stage 0.

What was copied, and what was not
=================================

Copied -- everything the application reaches:

``templates/jqm/``
    ``v1_1_0.html``, ``simple.html``, ``messages.html``, ``formfields.html``,
    ``login.html`` and ``logout.html``. ``kasvimuseo``'s two report templates
    extend ``jqm/simple.html``, and ``ylaneenkasvit/urls.py`` names
    ``jqm/login.html`` and ``jqm/logout.html``; the other three are reached
    from those by ``{% extends %}`` and ``{% include %}``.

``static/css/jqm-django.css``, ``static/js/jqm-django.js``
    Both are named by ``v1_1_0.html``, so every page built on these templates
    asks for them.

Left behind:

``templates/jqm/form.html``
    The seventh template. It renders a whole form page for a generic view;
    nothing in this repository extends, includes or names it, and no view
    passes the ``title``, ``form`` and ``submit`` context it wants. Copying it
    would have been carrying a page the site does not have.

``models.py``, ``views.py``, ``tests.py``
    The three near-empty modules. ``models.py`` and ``views.py`` are the
    ``startapp`` stubs with nothing in them but their "Create your ... here"
    comments, and ``tests.py`` is the scaffolding ``TestCase`` asserting that
    1 + 1 is 2. Django 1.5 does not require an app to have a ``models`` module,
    so ``'jqm'`` stays in ``INSTALLED_APPS`` -- which is what the app-directory
    template loader and the ``staticfiles`` app-directories finder read -- with
    none of them present.

``doc/``, ``images/``, ``setup.py``, ``MANIFEST.in``, ``README.rst``
    Upstream's own documentation and packaging. The packaging is what this
    repository's ``setup.py`` and ``MANIFEST.in`` now do instead.

One thing vendoring does *not* change
=====================================

``v1_1_0.html`` loads jQuery 1.7.2 and jQuery Mobile 1.1.0 from
``code.jquery.com``. That is a page asset fetched by the visitor's browser, not
a build input, so it is untouched by issue 031 and by this copy: the image
builds and the production install now need no network beyond PyPI, and a page
rendered from these templates still asks the CDN for its scripts. Bringing
those two files in as well would be a separate change with a different
argument.
