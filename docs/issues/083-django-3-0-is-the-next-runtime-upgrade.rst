Issue 083: Django 3.0 is the next runtime upgrade step
======================================================

:Status: Open
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 14
:Evidence: Stage 14 lists the removed APIs and compatible package versions.
:Depends on: 082
:Blocks: 084
:Related: 036 -- the runtime upgrade programme
:Decision: undecided
:Resolution: (none)

Work
----

This issue is for the implementation agent. It tracks Stage 14 of :doc:`../upgrade-plan`.

Move the project to Django 3.0.14 after issue 082. Replace the three
``render_to_response`` calls with ``render(request, …)`` in
``kasvimuseo/views.py`` and remove the unused ``RequestContext`` import. Use
the PostgreSQL backend name supported by Django 3.0. Check whether any
remaining dependency uses ``django.utils.six``. Update Photologue to 3.11 and
Grappelli to 2.14.2. Keep ``psycopg2-binary`` below 2.9.

Checks
------

Run the repository test suite, build both images, check their installed package
sets, run Django's system and migration checks, and build the documentation.
Record the commands and results here.
