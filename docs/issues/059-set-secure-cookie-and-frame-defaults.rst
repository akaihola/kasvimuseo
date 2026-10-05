Issue 059: Set secure cookie and frame defaults
===============================================

:Status: Fixed
:Severity: High
:Area: settings / security
:Reported: 2026-08-02
:Source: Repository maintenance
:Evidence: The settings enable secure cookies and a frame policy. Local development and tests override the cookie flags for HTTP.
:Depends on: (none)
:Blocks: (none)
:Related: 057 -- related work
    025 -- related work
    049 -- related work
    051 -- related work
    019 -- related work
:Decision: Keep the generic implementation and its automated checks.
:Resolution: 72008933932b records the implementation.

Scope
-----

This record helps maintainers locate the work. The settings enable secure cookies and a frame policy. Local development and tests override the cookie flags for HTTP.

The private deployment repository owns installation-specific evidence and operations follow-up.
