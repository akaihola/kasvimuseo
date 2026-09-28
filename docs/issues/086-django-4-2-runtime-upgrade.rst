Issue 086: Django 4.2 is the next runtime upgrade step
======================================================

:Status: In progress
:Claimed: feature/upgrade-django-to-4-bq0
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-28
:Source: Backlog refill from upgrade plan Stage 17
:Evidence: Stage 17 names Django 4.2 LTS and its package compatibility requirements.
:Depends on: 085
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 17 through Django 4.0 and 4.1, then move to Django 4.2 on Python 3.12.
:Resolution: (none)

Work
----

This issue is for the implementation agent. It tracks Stage 17 of :doc:`../upgrade-plan`.

Move the project from Django 3.2 through Django 4.0.10 and 4.1.13 to Django
4.2.30 LTS after issue 085. Replace removed translation and text APIs, remove
``pytz``, update compatible dependencies, and move Python to 3.12. At Django
4.2, replace the removed storage settings with ``STORAGES``.

Checks
------

Run the repository test suite, build both images, check their installed package
sets, run Django's system and migration checks, and build the documentation.
Record the commands and results here.
