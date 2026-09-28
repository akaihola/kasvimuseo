Issue 087: Django 5.2 is the next runtime upgrade step
======================================================

:Status: In progress
:Claimed: feature/upgrade-to-django-5-530
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 18
:Evidence: The dependency plan resolves Django 5.2.16. The application still runs Django 4.2; verify both runtime images and checks.
:Depends on: 086
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: undecided
:Resolution: (none)

Work
----

This issue tracks Stage 18 of :doc:`../upgrade-plan`.

Move the project from Django 4.2 to Django 5.2.16 LTS after issue 086. Keep
Python 3.12. Update ``django-grappelli`` to 4.0.4 and ``django-photologue``
to 3.19. Keep ``django-sortedm2m`` at 4.0.0 and ``pytest-django`` at 4.11.1.
Update the resolved package locks. Remove ``DEFAULT_FILE_STORAGE``,
``STATICFILES_STORAGE`` and ``index_together`` because Django 5.1 removes them.

Checks
------

Build both images. Confirm that their installed packages match the committed
locks. Run the application tests, browser tests, Django system check, migration
checks and documentation build. Record the commands and results here.
