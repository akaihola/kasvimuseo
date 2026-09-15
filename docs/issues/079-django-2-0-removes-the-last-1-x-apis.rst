Issue 079: Django 2.0 removes the last 1.x APIs this project uses
=================================================================

:Status: In progress
:Claimed: 0712fb6b-a155-4292-aa9b-ce9b96906978, feature/upgrade-django-from-85f
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-15
:Source: Backlog refill from upgrade plan Stage 11
:Evidence: The suite on Django 1.11.29 prints ``RemovedInDjango20Warning`` for ``allow_tags``, ``use_for_related_fields`` and a 3-tuple ``include()``.
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 11 on Python 3.7 with the pins the upgrade plan names. Keep the later stages in issue 036.
:Resolution: Pending on the claiming branch.

Work
----

This issue is for the implementation agent. It tracks Stage 11 of :doc:`../upgrade-plan`.

Django 2.0 removes three things the code still uses:

#. ``allow_tags`` on three ``ModelAdmin`` methods in ``kasvimuseo/admin.py``.
#. ``use_for_related_fields`` on ``ObservationManager`` in ``kasvimuseo/models.py``.
#. ``include(admin.site.urls)`` in ``ylaneenkasvit/urls.py``, a 3-tuple include.

The stage also moves the pins: Django 2.0.13, grappelli 2.11.2, photologue 3.8.1 and sortedm2m 1.5.0.
Python stays at 3.7.
