==================================================================
Issue 023: django.contrib.messages is configured but not installed
==================================================================

:Status: Fixed
:Severity: Medium
:Area: settings / Django upgrade
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``kasvimuseo/tests/test_settings_messages.py`` -- added with the fix;
    before it there was none
:Depends on: 019 -- ``Fixed``: the middleware list now exists and already
    carries ``MessageMiddleware``, so what is left here is the
    ``INSTALLED_APPS`` entry alone
:Blocks: 036 -- required from Stage 5 (Django 1.7)
:Related: 019 -- the same class of problem, same file
:Decision: Add ``'django.contrib.messages'`` to ``INSTALLED_APPS``. There was
    no second option to weigh: issue 019 had already supplied the middleware
    half, by writing the Django 1.5 default -- ``MessageMiddleware`` included --
    out into ``common_settings``, so the app entry was all that was left of this
    issue. It changes nothing that runs today and is required by the admin's
    system checks from Django 1.7, Stage 5 of the upgrade plan.
:Resolution: 386f88c -- the ``INSTALLED_APPS`` entry in
    ``ylaneenkasvit/common_settings.py``, the test that pins it, and the
    upgrade plan's two now-stale sentences about it

Problem
=======

``ylaneenkasvit/common_settings.py`` lists

::

    'django.contrib.messages.context_processors.messages'

in ``TEMPLATE_CONTEXT_PROCESSORS``, but ``django.contrib.messages`` is **not**
in ``INSTALLED_APPS``. Its middleware is: ``MessageMiddleware`` is in the
Django 1.5 default and has always been running, and since issue 019 it is
written out in the file rather than inherited. The app is the missing half.

Django 1.5 tolerates this. From 1.7 the admin's system checks require the
messages app, and the admin is this application.

Impact
======

Latent. The context processor currently has nothing to do, so nothing visibly
fails; the admin's own messages ("The species was added successfully") are
delivered through the same framework and will start depending on it being
present. At Django 1.7 the system check turns this into a hard startup error --
which is the good outcome, since the alternative is silently losing admin
confirmation messages.

Options
=======

Add ``'django.contrib.messages'`` to ``INSTALLED_APPS``. That is now the whole
of it: issue 019 wrote ``MIDDLEWARE_CLASSES`` out as the 1.5 default, which
includes ``MessageMiddleware``, so the middleware half is done and this line is
the last piece missing before Stage 5 (Django 1.7). It costs nothing before
then.

Decision
========

Done as described above: one line in ``INSTALLED_APPS``, placed with the other
``django.contrib.*`` entries. Nothing else in the file was touched -- its other
open issues (024's ``TEMPLATE_DIRS``, 020's ``indexer`` and ``paging``, 021's
``gunicorn``, 026's absent ``ALLOWED_HOSTS``) are still there and still open.

The framework is now configured in all three places rather than two, and
``kasvimuseo/tests/test_settings_messages.py`` pins that, so dropping one of
them again is a deliberate act.

**No table and no migration**, which was checked rather than assumed.
``MESSAGE_STORAGE`` is unset in this project, so it is Django's default,
``django.contrib.messages.storage.fallback.FallbackStorage`` -- a cookie, with
the session as the fallback. ``django.contrib.messages.models`` exists but is
empty (``get_models(get_app('messages')) == []``), which is why ``syncdb`` and
South have nothing to do with the app: ``dev/kasvimuseo db bootstrap`` was run
with the entry in place and created no new relation. The test asserts both, so
a later stage that changes the storage backend has to notice.

**The banner was watched, not inferred.** The confirmation message is the thing
this issue is about, so it was produced end to end against the real settings
module (``ylaneenkasvit.ylaneenkasvit_settings``) and the development database:
gunicorn under ``dev/kasvimuseo app run``, a logged-in superuser, a species
added through ``/admin/kasvimuseo/species/add/``, the 302 to the changelist
followed, and on that page

::

    <ul class="grp-messagelist">
    <li class="grp-info">kasvilaji &quot;kurjenmiekka-e2e&quot; on lisätty.</li>

-- in Finnish, so ``LANGUAGE_CODE`` and the translations issue 040 restored are
in the path too. The same flow driven from ``django.test.client`` inside
``manage.py shell`` produces the English wording instead, because a management
command deactivates translations; the message itself is the same one.
``kasvimuseo/tests/test_admin.py``'s
``test_planted_species_report_through_the_admin`` covers the other direction,
``message_user`` from an admin action, and its docstring no longer says the app
is missing.

See also
========

Issue 019 -- the same class of problem, and the fix touches the same file.
``docs/upgrade-plan.rst``, Stage 0.
