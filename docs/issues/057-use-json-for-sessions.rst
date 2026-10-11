Issue 057: Use JSON for sessions
================================

:Status: Fixed
:Severity: High
:Area: settings / security
:Reported: 2026-08-02
:Source: Repository maintenance
:Evidence: The settings select the JSON session serializer. Tests reject session data that requires pickle deserialization.
:Depends on: (none)
:Blocks: (none)
:Related: 025 -- related work
    036 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: 41774eb records the implementation.

Scope
-----

This record helps maintainers locate the work. The settings select the JSON session serializer. Tests reject session data that requires pickle deserialization.

The private deployment repository owns installation-specific evidence and operations follow-up.
