Issue 026: Read allowed hosts from the environment
==================================================

:Status: Fixed
:Severity: Medium
:Area: settings / deployment
:Reported: 2026-07-28
:Source: Repository maintenance
:Evidence: The settings read allowed host names from a required environment variable. Tests cover accepted and rejected hosts.
:Depends on: (none)
:Blocks: 051 -- related work
:Related: 025 -- related work
    049 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: df16cc1 records the implementation.


Scope
-----

This record helps maintainers locate the work. The settings read allowed host names from a required environment variable. Tests cover accepted and rejected hosts.

The private deployment repository owns installation-specific evidence and operations follow-up.
