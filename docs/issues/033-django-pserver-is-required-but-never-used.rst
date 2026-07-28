=========================================================
Issue 033: django-pserver is required but never used
=========================================================

:Status: Open
:Severity: Low
:Area: dependencies / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``requirements/dev.txt`` lists ``django-pserver``. The only mention of it
anywhere else in the repository is a commented-out line, present in both
``ylaneenkasvit/local_settings.development.py`` and the untracked
``local_settings.py`` template::

    #settings['INSTALLED_APPS'] += 'pserver', 'django_extensions',

So it is installed on every development machine and has never been enabled.

The package has exactly one release on PyPI, ``0.2``, with no
``Requires-Python`` and no declared dependencies. It provides a threaded
``runserver``; ``django-extensions``' ``runserver_plus`` -- already in
``dev.txt``, along with the ``Werkzeug`` it needs -- covers the same ground.

Impact
======

Negligible. Filed for completeness, because the alternative is that whoever
does the upgrade spends time establishing whether a single-release package from
2011 has a Python 3 story.

Options
=======

Remove it from ``dev.txt`` and delete the commented-out line, or uncomment the
line if the threaded server is actually wanted -- in which case say so, because
right now the configuration says it is not.

See also
========

``docs/upgrade-plan.rst`` Part 5.
