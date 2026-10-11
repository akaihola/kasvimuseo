Issue 065: Write application errors to stderr
=============================================

:Status: Fixed
:Severity: Medium
:Area: settings / operations
:Reported: 2026-08-02
:Source: Repository maintenance
:Evidence: The settings write application errors to stderr. Tests check logging without relying on an external mail service.
:Depends on: (none)
:Blocks: (none)
:Related: 044 -- related work
    025 -- related work
    026 -- related work
    057 -- related work
    059 -- related work
    036 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: a5d6efd records the implementation.


Scope
-----

This record helps maintainers locate the work. The settings write application errors to stderr. Tests check logging without relying on an external mail service.

The private deployment repository owns installation-specific evidence and operations follow-up.
