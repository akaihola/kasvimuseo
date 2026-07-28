==================================================================
Issue 023: django.contrib.messages is configured but not installed
==================================================================

:Status: Open
:Severity: Medium
:Area: settings / Django upgrade
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``ylaneenkasvit/common_settings.py`` lists

::

    'django.contrib.messages.context_processors.messages'

in ``TEMPLATE_CONTEXT_PROCESSORS``, but ``django.contrib.messages`` is **not**
in ``INSTALLED_APPS``, and neither is its middleware (see issue 019 -- no
middleware is configured at all).

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

Add ``'django.contrib.messages'`` to ``INSTALLED_APPS``, and add
``MessageMiddleware`` when issue 019 is addressed. Both are prerequisites of
Stage 5 (Django 1.7) and cost nothing before then.

See also
========

Issue 019 -- the same class of problem, and the fix touches the same file.
``docs/upgrade-plan.rst``, Stage 0.
