Issue 068: Provide an optional development login
================================================

:Status: Fixed
:Severity: Low
:Area: development workflow / authentication
:Reported: 2026-08-03
:Source: Repository maintenance
:Evidence: The development helper enables a login route for active local accounts. Tests check that other settings do not expose the route.
:Depends on: (none)
:Blocks: (none)
:Related: 067 -- related work
    052 -- related work
    026 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: f44adf0 records the implementation.

Scope
-----

This record helps maintainers locate the work. The development helper enables a login route for active local accounts. Tests check that other settings do not expose the route.

The private deployment repository owns installation-specific evidence and operations follow-up.
