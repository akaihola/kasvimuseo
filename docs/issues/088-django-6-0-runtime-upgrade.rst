Issue 088: Django 6.0 is the next runtime upgrade
=================================================

:Status: In progress
:Claimed: feature/upgrade-django-to-6-0ao
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 19
:Evidence: The dependency plan resolves Django 6.0.7. Verify both runtime images and checks after issue 087.
:Depends on: (none)
:Blocks: (none)
:Related: 036, 087 -- the runtime upgrade programme; 087 is Stage 18
:Decision: undecided
:Resolution: (none)

Work
----

This issue tracks Stage 19 of :doc:`../upgrade-plan`.

Move the project from Django 5.2 to Django 6.0.7 on Python 3.12 or later. Keep
``DEFAULT_AUTO_FIELD`` set to ``AutoField`` or plan the database change to
``BigAutoField``. Use ``psycopg2 >= 2.9.9`` or psycopg 3. Update Grappelli to
5.0.0 and Photologue to 3.20. Remove ExifRead from the production dependencies.
Keep ``django-extensions`` development-only because version 4.1 does not claim
Django 6.0 support.

Checks
------

Build both images. Confirm that their installed packages match the committed
locks. Run the application tests, browser tests, Django system check, migration
checks and documentation build. Record the commands and results here.
