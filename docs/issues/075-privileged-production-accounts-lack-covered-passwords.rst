================================================================================
Issue 075: Privileged production accounts lack covered passwords
================================================================================

:Status: Open
:Severity: High
:Area: deployment / security
:Reported: 2026-08-26
:Source: Maintenance window report in ``docs/issues/incoming.rst``
:Evidence: The production audit lists active privileged accounts ``hl``,
    ``sirkku`` and ``tuula`` whose passwords are absent from the vault. The
    inactive staff account ``anja`` still has its staff flag. The deployment
    data named ``kasvimuseo_admin_passwords`` can rotate the passwords, but the
    account and flag decisions remain open.
:Depends on: (none)
:Blocks: (none)
:Related: 050 -- the existing admin password rotation
    049 -- the security maintenance window that can apply the rotation
:Decision: undecided
:Resolution: (none yet)

Problem
-------

The project cannot verify or rotate every privileged production account.
Unknown passwords and stale staff flags increase the cost of a compromise.

What remains
------------

The maintainer must decide which accounts remain active and which flags remain.
The deployment owner must add approved passwords to the vault and rotate them.
The owner must record the result without writing passwords in this repository.
