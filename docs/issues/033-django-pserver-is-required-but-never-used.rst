====================================================
Issue 033: django-pserver is required but never used
====================================================

:Status: Fixed
:Severity: Low
:Area: dependencies / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: (none)
:Blocks: 036 -- Stage 0
:Related: (none)
:Decision: Remove it from ``requirements/dev.txt`` and delete the commented-out line. The threaded server is not wanted: nothing has enabled it in fifteen years, and ``django-extensions``' ``runserver_plus`` is already installed for the same job. The ``django_extensions`` the same comment names is kept -- it is in ``INSTALLED_APPS`` already, so the comment offered a worse way to get something the project has.
:Resolution: 0c82b49 -- with issues 020 and 021, which edit the same six lines

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

Decision
========

The first option: the line is gone from ``requirements/dev.txt`` and the
commented-out line is gone from
``ylaneenkasvit/local_settings.development.py``. It went in with issues 020 and
021, which edit the same two requirements files and the same settings package.

**Deleting the comment loses nothing.** It named two apps, and they are in
opposite positions:

``pserver``
    Never enabled, and now not installed. Its threaded ``runserver`` is covered
    by ``django-extensions``' ``runserver_plus``, whose ``Werkzeug`` is already
    in ``dev.txt`` -- so the capability the line offered is still one command
    away, by a package with releases after 2011.

``django_extensions``
    **Wanted, and already installed properly.** It is in
    ``ylaneenkasvit/common_settings.py``'s ``INSTALLED_APPS``, in every
    environment, and in both ``requirements/production.txt`` and
    ``requirements/dev.txt``. Appending it again from a local settings file
    would have been a second, worse way to get what the project already has --
    which is presumably why the line was commented out rather than used. No
    replacement comment is needed, because there is nothing left to say that
    ``INSTALLED_APPS`` does not say already.

    It is not removed from anywhere here. ``docs/upgrade-plan.rst`` Stage 0 does
    want it out of *production*, which is a different change and still
    outstanding.

One loose end, and it is not in the repository: ``local_settings.py`` is
untracked, and ``dev/kasvimuseo`` copies it from
``local_settings.development.py`` only when there is none, so a development
machine set up before today keeps its own copy of the line. It stays commented
out there and does nothing; it would only matter if somebody uncommented it,
and then it would fail loudly on the missing ``pserver`` rather than quietly.
Nothing is added to warn about it -- the script's one such warning exists
because ``MEDIA_FALLBACK_URL``'s absence is silent and wrong (issue 048), which
this is not.

Verification
============

Shared with issues 020 and 021, and written out in full in issue 020.
``pserver`` is the one of the three that the development image never had:
``dev/Containerfile`` installs ``requirements/production.txt`` and the test
pins, not ``dev.txt``, so ``dev.txt`` is what a developer installs by hand.
After the change, ``git grep -n "pserver" -- . ':!docs'`` prints nothing, and
the rebuilt image, the suite (406 passed) and the pages are as recorded in 020.

See also
========

``docs/upgrade-plan.rst`` Part 5.
