========================================================
Issue 020: django-indexer and django-paging are unused
========================================================

:Status: Open
:Severity: Low
:Area: dependencies / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none -- ``grep -rn "indexer\|paging" --include='*.py' --include='*.html'`` matches only ``INSTALLED_APPS``)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``requirements/production.txt`` pins ``django-indexer==0.3.0`` and
``django-paging==0.2.4``, and ``ylaneenkasvit/common_settings.py`` lists
``indexer`` and ``paging`` in ``INSTALLED_APPS``.

Nothing else in the repository mentions either one -- not a Python import, not
a template tag, not a template. Both are early Sentry dependencies that came
along with a long-removed integration; ``common_settings.py`` still carries the
``# TODO: configure raven`` comment from the same era.

Neither has been released since 2012.

Impact
======

Two abandoned packages installed and initialised on every request path for no
reason. Each is also an obstacle in the upgrade: any package in
``INSTALLED_APPS`` has to keep loading under every future Django version, and
these two will not.

Options
=======

Remove both from ``production.txt`` and from ``INSTALLED_APPS``. Removing an
app that contributes no models and no migrations has no database consequence.

Worth doing before the upgrade starts rather than during it -- see
``docs/upgrade-plan.rst``, Stage 0, which groups this with the other
zero-risk removals.
