Issue 082: Django 2.2 is the next runtime upgrade step
======================================================

:Status: Open
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 13
:Evidence: Stage 13 names the package versions and separate Python runtime change.
:Depends on: (none)
:Blocks: 083
:Related: 036 -- the runtime upgrade programme
:Decision: undecided
:Resolution: (none)

Work
----

This issue is for the implementation agent. It tracks Stage 13 of :doc:`../upgrade-plan`.

Update the runtime to Django 2.2.28, Grappelli 2.13.4, Photologue 3.10,
sortedm2m 2.0.0 and a compatible pytest-django release. Move Python from 3.7
to 3.9 in a separate commit from the Django upgrade. Keep the package locks in
step with the pins.

Checks
------

Run the repository test suite, build both images, check their installed package
sets, run Django's system and migration checks, and build the documentation.
Record the commands and results here.
