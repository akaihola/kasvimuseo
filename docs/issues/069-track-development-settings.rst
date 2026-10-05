Issue 069: Track development settings
=====================================

:Status: Fixed
:Severity: High
:Area: dev environment / settings
:Reported: 2026-08-03
:Source: Repository maintenance
:Evidence: The development helper selects tracked development settings. Optional local overrides apply only to that development environment.
:Depends on: (none)
:Blocks: (none)
:Related: 059 -- related work
    048 -- related work
    044 -- related work
    050 -- related work
    025 -- related work
    026 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: c37eb1f records the implementation.


Scope
-----

This record helps maintainers locate the work. The development helper selects tracked development settings. Optional local overrides apply only to that development environment.

The private deployment repository owns installation-specific evidence and operations follow-up.
