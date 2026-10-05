Issue 067: Distinguish database bootstrap from restore
======================================================

:Status: Fixed
:Severity: Medium
:Area: development tooling
:Reported: 2026-08-03
:Source: Development command review
:Evidence: The database helper distinguishes bootstrap from restore.
:Depends on: (none) -- one guard in a ``case`` arm and one new command, both
    in ``dev/kasvimuseo``
:Blocks: (none)
:Related: 050, 055, 068, 069
:Decision: Reject dump arguments to bootstrap. Require restore for an existing database.
:Resolution: 9fa70bf records the implementation.

Work
----

This issue helps developers choose the database command. Bootstrap creates an empty database, while restore loads a supplied dump.

The private deployment repository owns the original operations report.
