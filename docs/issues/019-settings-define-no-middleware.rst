========================================
Issue 019: Settings define no MIDDLEWARE
========================================

:Status: Fixed
:Severity: High
:Area: settings / Django upgrade
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``kasvimuseo/tests/test_settings_middleware.py`` -- added with the fix; before it there was none, and ``grep -rn MIDDLEWARE kasvimuseo ylaneenkasvit`` returned nothing
:Depends on: (none)
:Blocks: 023 -- the middleware list it needs now exists, and already carries
    ``MessageMiddleware``; what is left there is the ``INSTALLED_APPS`` entry
    036 -- silent loss of the middleware stack at Stage 11
:Related: 023 -- the other missing-settings landmine, same file
:Decision: Write the Django 1.5 default out into ``common_settings`` verbatim,
    read from the ``global_settings.py`` of the installed 1.5.1 rather than from
    upstream's current source, and keep the old name. The rename to
    ``MIDDLEWARE`` waits for Stage 8 (Django 1.10), which is the first release
    that honours it -- doing it now would be a setting Django 1.5 ignores, which
    is the same silence this issue is about, only sooner.
:Resolution: RESOLUTION_COMMIT

Problem
=======

``ylaneenkasvit/common_settings.py`` never defines ``MIDDLEWARE_CLASSES`` or
``MIDDLEWARE``. The site runs entirely on the default in Django's
``global_settings``.

That default is being withdrawn. Read out of the shipped ``global_settings.py``
of each release:

========= ======================== ==================
Django    ``MIDDLEWARE_CLASSES``   ``MIDDLEWARE``
========= ======================== ==================
1.5 – 1.8 populated tuple          absent
1.9       populated list           absent
1.10–1.11 populated list           ``None``
**2.0** + **removed**              ``[]``
========= ======================== ==================

At Django 2.0 the project would therefore start with **no middleware at all**:
no sessions, no authentication, no CSRF, no messages. The admin -- which is
this application -- would not work, and nothing would raise an error naming the
cause.

Impact
======

A silent, total loss of the middleware stack at Django 2.0. It is listed as
High not because it is hard to fix but because the failure gives no useful
signal, and it sits eleven stages into a long upgrade where attention will be
elsewhere.

Options
=======

Write ``MIDDLEWARE_CLASSES`` out explicitly **now**, as a verbatim copy of the
Django 1.5 default. Today that is a no-op, which is exactly why it is safe to
do at any time. It converts a future silent breakage into a visible line of
configuration that later stages can edit.

The rename to ``MIDDLEWARE`` follows at Django 1.10, where both spellings are
honoured -- see ``docs/upgrade-plan.rst``, Stage 8.

Decision
========

Done as described above. The tuple was read out of the ``global_settings.py``
of the Django in the application container -- 1.5.1, the pin in
``requirements/production.txt`` -- rather than from memory or from upstream's
current source, since the whole value of the change is that it copies *this*
project's effective configuration and not a later one::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )

The two entries 1.5 ships commented out -- ``ConditionalGetMiddleware`` and
``GZipMiddleware`` -- are not copied: they are not part of the value, and
carrying upstream's commented-out lines into this file would read as a choice
this project had made.

It stays a tuple, matching ``INSTALLED_APPS`` and
``TEMPLATE_CONTEXT_PROCESSORS`` in the same file, and it keeps the name
``MIDDLEWARE_CLASSES``. Renaming it to ``MIDDLEWARE`` belongs to Stage 8
(Django 1.10), the first release that reads that name; written today it would
be a setting Django 1.5 silently ignores, which is this issue's own failure
mode.

``MessageMiddleware`` is in the list because it is in the 1.5 default and has
therefore been running all along -- not because anything was added for issue
023. That issue's remaining work is the ``INSTALLED_APPS`` entry; its middleware
line is already here, in the list this change created.

Nothing else in the settings needed anything. ``ylaneenkasvit_settings.py``,
``kajala_settings.py`` and ``test_settings.py`` all do ``from .common_settings
import *`` and none of them mentions middleware, and neither does
``local_settings.development.py``, whose ``modify()`` rewrites only the
database, paths and ``ALLOWED_HOSTS``; each was loaded and checked rather than
assumed.

That the change is a no-op today was measured rather than argued: the
middleware Django actually applies is byte-for-byte the same list before and
after, under every settings module that can be loaded, and
``kasvimuseo/tests/test_settings_middleware.py`` keeps that pinned. It is a
test expected to be changed deliberately later -- the list grows at Stage 5 and
is renamed at Stage 8 -- which is the convention the rest of this register
follows.

See also
========

``docs/upgrade-plan.rst`` Part 3, "Two settings landmines that a grep does not
show, because the settings are *missing*". Issue 023 is the other one.
