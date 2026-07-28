====================================================================
Issue 021: gunicorn is an INSTALLED_APP for a command that is gone
====================================================================

:Status: Open
:Severity: Low
:Area: settings / dependencies
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``ylaneenkasvit/common_settings.py`` lists ``gunicorn`` in ``INSTALLED_APPS``.

A WSGI server is not a Django application. It was listed there for one reason:
gunicorn used to ship a ``run_gunicorn`` management command, which only worked
if the package was an installed app.

That command no longer exists. Checking the shipped contents of each release:

=================== ===========================================
gunicorn            ``management/commands/run_gunicorn.py``
=================== ===========================================
0.17.4 (pinned)     present
18.0 – 19.6.0       present
**19.7.1** +        **removed**
=================== ===========================================

The project does not use the command in any case -- ``ylaneenkasvit/wsgi.py``
is the entry point, and the Dockerfile runs ``manage runserver``.

Impact
======

Harmless today, but it is dead configuration that will confuse whoever does the
upgrade, and gunicorn ≥ 19.7.1 has no ``management`` package at all.

Options
=======

Remove ``'gunicorn'`` from ``INSTALLED_APPS``. Keep the dependency itself --
it is still the production server.

See also
========

Issue 029 covers a real gunicorn constraint, as distinct from this cosmetic one.
