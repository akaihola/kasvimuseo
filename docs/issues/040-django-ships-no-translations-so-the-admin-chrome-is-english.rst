=======================================================================
Issue 040: Django ships no translations, so the admin chrome is English
=======================================================================

:Status: Open
:Severity: Medium
:Area: packaging / i18n
:Reported: 2026-07-28
:Source: Dashboard walkthrough, branch ``dashboard-usability``
:Evidence: (none -- the suite asserts on the project's own strings, which do translate)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``LANGUAGE_CODE`` is ``fi`` and the project translates its own strings, but
every string Django itself provides renders in English. On the admin front
page that is the ``Site administration`` heading, the ``Add`` and ``Change``
links on every model row, and the ``Groups`` and ``Users`` model names --
next to ``Kasvilajit``, ``Penkit``, ``Raportit ja työkalut`` and the rest in
Finnish.

The cause is not configuration. Django 1.5.1's ``setup.py`` lists its
non-Python files -- locale catalogs, fixtures, ``project_template``,
``contrib/admin/bin`` -- in ``data_files`` rather than ``package_data``.
Modern pip builds a wheel from that sdist, and a wheel installs ``data_files``
relative to the install prefix instead of into the package. In the dev image::

    /usr/local/lib/python2.7/site-packages/django/conf/locale/fi/  formats.py only
    /usr/local/django/conf/locale/fi/LC_MESSAGES/django.mo         14.2 kB, unreachable

``django/contrib/admin/locale/`` does not exist under ``site-packages`` at all;
its 2571 data files, Finnish included, all landed under ``/usr/local/django/``.
``gettext`` only looks inside the package, so the catalogs are installed but
never loaded.

Both images are affected: ``dev/Containerfile`` and the production
``Dockerfile`` install from ``requirements/production.txt`` the same way, and
the production build then copies ``/install`` (which contains the same stray
``django/`` tree) to ``/usr/local``.

photologue's model names -- ``Galleries``, ``Photos`` -- are English for a
different reason: photologue 2.8 ships no ``fi`` catalog at all.

Impact
======

Cosmetic but constant, and it lands on the page the application opens on. The
users are Finnish-speaking gardeners, and the admin is the whole application:
there is no separate front end to log into. Half-translated chrome is worse
than either extreme, because ``Add``/``Change`` sit on the same row as the
Finnish model names.

Options
=======

1. Move the stray tree back where ``gettext`` looks, in both image
   definitions -- one line after the ``pip install``::

       cp -a /usr/local/django/. \
             /usr/local/lib/python2.7/site-packages/django/

   Cheapest, and it also restores the fixtures and ``project_template`` that
   went astray with the catalogs. It has to be repeated in the production
   ``Dockerfile``, where the copy has to happen in the ``builder`` stage or
   against ``/install``.

2. ``pip install --no-binary django``, which makes pip run the sdist's
   ``setup.py install`` and place the data files correctly. One flag, but it
   applies to the whole requirements file unless it is split.

3. Do nothing until the upgrade plan retires Django 1.5. Modern Django ships
   its catalogs as package data, so this fixes itself at that point -- see
   issue 036 for how far away that is.

Whatever is chosen, ``Galleries``/``Photos`` still needs a decision of its own:
either translate the two msgids in a project-level catalog or leave photologue
in English.

See also
========

Issue 036 (the runtime stack is end of life), ``docs/upgrade-plan.rst``.
