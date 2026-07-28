==============================================================
Issue 022: Dead /media/grappelli/ route and ADMIN_MEDIA_PREFIX
==============================================================

:Status: Open
:Severity: Low
:Area: urls / settings / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: (none)
:Blocks: 036 -- Stage 0, and one of the three string-view routes Django 1.10 stops accepting
:Related: (none)
:Decision: undecided
:Resolution: (none yet)

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

See also
========

``docs/upgrade-plan.rst``, Stage 0.
