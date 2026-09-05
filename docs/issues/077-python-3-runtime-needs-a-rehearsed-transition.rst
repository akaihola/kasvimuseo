Issue 077: The Python 3 runtime needs a rehearsed transition
============================================================

:Status: Open
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-05
:Source: Backlog refill from upgrade plan Stage 10
:Evidence: ``requirements/production.txt`` pins Django 1.11.29; both images use Python 2.7.
:Depends on: 076 -- prepare model text first
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: undecided
:Resolution: (none yet)

Work
----

This issue is for the implementation agent. It defines the next bounded runtime change.

The next implementation agent must complete :doc:`../upgrade-plan`, Stage 10.

#. Check both images, installation paths, dependency locks, test backports, and the Ansible runtime.
#. Resolve the psycopg2-binary discrepancy between the lock and Stage 10.
#. Check official support information before selecting versions.
#. Run Python 3 tests and an isolated deployment rehearsal with backup and rollback checks.
#. Measure the starting runtime before deployment.

The lock specifies psycopg2-binary 2.8.4, but Stage 10 specifies 2.8.6.
Use an isolated database for the rehearsal.
Issue :doc:`078-planting-photo-text-reads-a-missing-attribute` tracks the remaining model defect.
