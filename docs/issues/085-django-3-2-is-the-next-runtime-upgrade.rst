Issue 085: Django 3.2 is the next runtime upgrade step
======================================================

:Status: In progress
:Claimed: Task d087b0fc-2e0d-45c4-bec5-2d297910fa85 on feature/upgrade-django-to-3-g5f
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 16
:Evidence: Stage 16 names Django 3.2 LTS and its package compatibility requirements.
:Depends on: 084
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 16 as requested. The Work section defines the runtime target.
:Resolution: (none)

Work
----

This issue is for the implementation agent. It tracks Stage 16 of :doc:`../upgrade-plan`.

Move the project to Django 3.2.25 after issue 084. Set
``DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'`` explicitly to prevent
Django 6.0 from changing the primary-key type. Update Grappelli to 2.15.7,
Photologue to 3.14, django-extensions to 3.1.5, and pytest-django to 4.5.2.
Move Python to 3.10 and keep the package locks in step with the pins.

Checks
------

Run the repository test suite, build both images, check their installed package
sets, run Django's system and migration checks, and build the documentation.
Record the commands and results here.
