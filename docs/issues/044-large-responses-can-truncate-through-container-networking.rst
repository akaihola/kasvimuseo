Issue 044: Large responses can truncate through container networking
====================================================================

:Status: Fixed
:Severity: High
:Area: dev environment / serving
:Reported: 2026-07-29
:Source: Repository maintenance
:Evidence: The development helper uses host networking and HTTP response framing. These settings prevent silent truncation through a port proxy.
:Depends on: (none)
:Blocks: (none)
:Related: 040 -- related work
    013 -- related work
    045 -- related work
    010 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: 70aedd7, 249ade0, 936b0aa records the implementation.

Scope
-----

This record helps maintainers locate the work. The development helper uses host networking and HTTP response framing. These settings prevent silent truncation through a port proxy.

The private deployment repository owns installation-specific evidence and operations follow-up.
