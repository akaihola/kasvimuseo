Issue 081: Django 2.1 is the next runtime upgrade step
======================================================

:Status: In progress
:Claimed: Kandev task 2dc5f07e-9976-4268-acb9-d7cdd9a2f6f6
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-27
:Source: Backlog refill from upgrade plan Stage 12
:Evidence: Stage 12 resolves to Django 2.1.15, Grappelli 2.12.4 and Photologue 3.9 on Python 3.7.
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 12 with Django 2.1.15, Grappelli 2.12.4 and Photologue 3.9. Keep Python 3.7.
:Resolution: (none yet)

Problem
=======

The project runs Django 2.0.13. Stage 12 of :doc:`../upgrade-plan` moves it to
Django 2.1.15. That stage also needs compatible Grappelli and Photologue pins.

Work
----

Update the runtime pins in ``requirements/production.in``,
``requirements/production.txt`` and ``requirements/dev.txt``. Use Django
2.1.15, Grappelli 2.12.4 and Photologue 3.9. Keep Python 3.7. Stage 12's
``login`` and ``logout`` removals were handled in Stage 9; do not repeat that
work.

Checks
------

Build both application images. Run the test suite, Django system check and
migration check on the new pins. Run ``dev/kasvimuseo docs``.

Update this issue with the decision and the commits that complete the stage.
