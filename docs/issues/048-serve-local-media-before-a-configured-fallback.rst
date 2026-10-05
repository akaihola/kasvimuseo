Issue 048: Serve local media before a configured fallback
=========================================================

:Status: Fixed
:Severity: Medium
:Area: dev environment / media
:Reported: 2026-07-29
:Source: Repository maintenance
:Evidence: The development server serves local media first. A developer can configure a fallback URL for missing files.
:Depends on: (none)
:Blocks: (none)
:Related: 044 -- related work
    011 -- related work
    028 -- related work
    042 -- related work
    022 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: c202290 records the implementation.

Scope
-----

This record helps maintainers locate the work. The development server serves local media first. A developer can configure a fallback URL for missing files.

The private deployment repository owns installation-specific evidence and operations follow-up.
