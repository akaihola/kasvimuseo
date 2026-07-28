========================================
Issue 019: Settings define no MIDDLEWARE
========================================

:Status: Open
:Severity: High
:Area: settings / Django upgrade
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none -- no test; ``grep -rn MIDDLEWARE kasvimuseo ylaneenkasvit`` returns nothing)
:Depends on: (none)
:Blocks: 023 -- ``MessageMiddleware`` needs a middleware list to go in
    036 -- silent loss of the middleware stack at Stage 11
:Related: 023 -- the other missing-settings landmine, same file
:Decision: undecided
:Resolution: (none yet)

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

See also
========

``docs/upgrade-plan.rst`` Part 3, "Two settings landmines that a grep does not
show, because the settings are *missing*". Issue 023 is the other one.
