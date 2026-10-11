Issue 025: Read secrets from the environment
============================================

:Status: Fixed
:Severity: High
:Area: security / settings
:Reported: 2026-07-28
:Source: Repository maintenance
:Evidence: The settings require explicit signing keys and database passwords. Missing variables stop startup.
:Depends on: (none)
:Blocks: (none)
:Related: 026 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: 49407ca, 90eb35d records the implementation.


Scope
-----

This record helps maintainers locate the work. The settings require explicit signing keys and database passwords. Missing variables stop startup.

The private deployment repository owns installation-specific evidence and operations follow-up.
