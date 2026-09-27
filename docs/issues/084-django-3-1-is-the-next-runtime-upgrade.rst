Issue 084: Django 3.1 is the next runtime upgrade step
======================================================

:Status: Open
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 15
:Evidence: Stage 15 identifies the psycopg2 boundary and compatible package versions.
:Depends on: 083
:Blocks: 085
:Related: 036 -- the runtime upgrade programme
:Decision: undecided
:Resolution: (none)

Work
----

This issue is for the implementation agent. It tracks Stage 15 of :doc:`../upgrade-plan`.

Move the project to Django 3.1.14 after issue 083. Confirm that the
``tzinfo_factory`` fix makes ``psycopg2-binary`` 2.9.x safe, then update
Grappelli to 2.14.4 and Photologue to 3.13. Keep the package locks in step
with the pins.

Checks
------

Run the repository test suite, build both images, check their installed package
sets, run Django's system and migration checks, and build the documentation.
Record the commands and results here.
