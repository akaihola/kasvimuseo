==============================================================
Issue 022: Dead /media/grappelli/ route and ADMIN_MEDIA_PREFIX
==============================================================

:Status: Fixed
:Severity: Low
:Area: urls / settings / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``test_the_admin_gets_its_grappelli_assets_from_staticfiles`` and
    ``test_media_under_grappelli_reaches_the_media_view`` in
    ``kasvimuseo/tests/test_project_urls.py``, added with the fix
:Depends on: (none)
:Blocks: 036 -- Stage 0, and one of the three string-view routes Django 1.10 stops accepting
:Related: 048 -- since that fix, ``/media/`` is a live prefix in development,
    and this dead route was declared ahead of the one serving it
:Decision: Delete both, which was the issue's only option. Nothing found
    contradicted it. The installed ``django-grappelli`` 2.4.5 in the container
    has no ``media/`` directory, so the route's ``document_root`` does not
    exist; the admin names its assets under ``STATIC_URL`` and gets them from
    ``staticfiles``, verified on a rendered admin page rather than only in the
    suite; the whole tree outside ``docs/`` had no other mention of either
    name, so no nginx or Ansible template was left pointing at the prefix; and
    the one consumer of ``ADMIN_MEDIA_PREFIX`` anywhere in the installed stack
    ignores its absence. See "What was checked" below.
:Resolution: Commit 1d08ee4 -- the route, its ``grappelli`` and ``os``
    imports, and ``ADMIN_MEDIA_PREFIX`` in all three site settings modules
    plus the commented example in ``common_settings.py``

Problem
=======

Two leftovers from Django 1.3-era static file handling.

**The URL route.** ``ylaneenkasvit/urls.py`` serves::

    (r'^media/grappelli/(?P<path>.*)', 'django.views.static.serve',
     {'document_root': os.path.join(os.path.dirname(grappelli.__file__),
                                    'media')}),

Listing the ``django-grappelli`` 2.4.5 sdist shows its package directory
contains ``static/``, ``templates/``, ``templatetags/``, ``views/``,
``dashboard/``, ``urls.py``, ``models.py`` and ``settings.py`` -- and **no**
``media/``. The route points at a directory that does not exist, so every
request under it 404s.

**The setting.** ``ADMIN_MEDIA_PREFIX`` is set in
``ylaneenkasvit_settings.py``, ``kajala_settings.py`` and ``test_settings.py``.
Django removed it in 1.4, superseded by ``STATIC_URL`` plus ``staticfiles``.
It has had no effect for the entire life of this codebase's current Django
version.

Impact
======

None at runtime -- this is dead weight, not a defect. It matters because the
route is one of the three string-view references in ``urls.py`` that Django
1.10 stops accepting, so somebody will otherwise spend time carefully porting
a route that should just be deleted.

Options
=======

Delete both. No replacement is needed: grappelli's assets are served from
``static/`` through ``staticfiles`` like everything else, which is already
configured.

What was checked
================

The option was taken, so the work was establishing that nothing depended on
either name. Five things, in the order they would have overturned the ruling.

**grappelli 2.4.5 as installed, not as packaged.** The issue read the sdist;
this read the container, since that is what the route resolves against::

    $ podman run --rm kasvimuseo-dev python -c "import grappelli, os; \
      p = os.path.dirname(grappelli.__file__); print(sorted(os.listdir(p)))"
    ['__init__.py', '__init__.pyc', 'dashboard', 'models.py', 'models.pyc',
     'settings.py', 'settings.pyc', 'static', 'templates', 'templatetags',
     'urls.py', 'urls.pyc', 'views']

No ``media/``. ``django.views.static.serve`` was being handed a
``document_root`` that does not exist, which is a 404 for every path under the
prefix.

**Nothing outside the documentation names either.**
``grep -rn 'media/grappelli\|ADMIN_MEDIA_PREFIX'`` over the whole tree --
templates, static CSS and JS, ``ansible/`` including the nginx and uwsgi
templates -- matched only ``ylaneenkasvit/urls.py``, the three settings
modules, the commented example in ``common_settings.py`` and these documents.
A leftover in a server config would have made this a live 404 rather than dead
weight; there is none.

**The setting has one consumer in the whole installed stack, and it is
indifferent.** ``django_extensions``' ``runprofileserver`` reads it with
``getattr(settings, 'ADMIN_MEDIA_PREFIX', None)`` to build the path list
``--nomedia`` skips. The value it was reading, ``STATIC_URL + 'grappelli/'``,
is a prefix of ``STATIC_URL``, which that same list already contains -- so even
the one reader loses nothing. Django itself dropped the setting in 1.4 and this
project runs 1.5.

**The admin gets its chrome from staticfiles, checked on a rendered page.**
Served with ``dev/kasvimuseo app run`` and logged in, ``/admin/`` returns 200
and names seven ``/static/grappelli/...`` assets; each of the six that is a
file answers 200 with its content -- ``screen.css`` at 167 158 bytes,
``jquery-ui-1.8.18.custom.min.js`` at 210 423. The seventh is
``/static/grappelli/`` itself, which is grappelli's own
``window.__admin_media_prefix__ = "/static/grappelli/"``: a string it fills
from ``{% static "grappelli/" %}`` in ``admin/base.html``, never from
``ADMIN_MEDIA_PREFIX``. The delivered page mentions ``media/grappelli``
nowhere.

**Removing the route cannot change where a real** ``/media/...`` **request
goes.** This is 048's concern. The two patterns are ``^media/grappelli/(?P<path>.*)``
and, added at the bottom of ``urls.py`` only when ``MEDIA_URL`` is a local
path, ``^media/(?P<path>.*)$``. Django tries them in declaration order, so the
deleted one was reachable *only* for paths beginning ``media/grappelli/``;
every other ``/media/`` request already fell through to ``serve_media`` and its
match is unaffected by what is no longer above it. For the shadowed prefix
itself the change is 404 into a working route: photologue stores uploads under
``photologue/photos/``, no ``grappelli/`` directory exists under any
``MEDIA_ROOT``, and a request there now gets the ordinary local-file-then-
fallback treatment instead of a guaranteed miss.
``test_media_under_grappelli_reaches_the_media_view`` pins that, and the four
``/media/`` tests 048 left behind still pass unchanged.

What Stage 0 may now assume
===========================

``docs/upgrade-plan.rst``, Stage 0 lists this deletion as work; it is done, and
the plan says so. Two later stages inherit the consequence:

* **Stage 8's** ``urls.py`` port has one string-view reference fewer to
  convert, and a correction came with counting them. The plan's removal table
  said three, from before issue 048; there were four by the time this was
  fixed, and the three now left are ``django.contrib.auth.views.login``,
  ``.logout`` and ``ylaneenkasvit.media.serve_media`` -- not the three the
  plan meant. Both places are updated. Django 1.10's removal of string views
  no longer reaches this route, and no later stage has to decide what a
  ``/media/grappelli/`` prefix pointing at nothing was for.
* ``ADMIN_MEDIA_PREFIX`` is gone from the settings, so no stage has to notice
  that a setting removed in Django 1.4 is still being assigned. The commented
  example in ``common_settings.py`` went with it, since a template for a new
  installation should not offer a setting nothing reads.

See also
========

``docs/upgrade-plan.rst``, Stage 0.
