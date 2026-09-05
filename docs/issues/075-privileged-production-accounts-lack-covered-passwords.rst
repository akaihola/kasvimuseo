================================================================================
Issue 075: Privileged production accounts lack covered passwords
================================================================================

:Status: Fixed
:Severity: High
:Area: deployment / security
:Reported: 2026-08-26
:Source: Maintenance window report in ``docs/issues/incoming.rst``
:Evidence: The production audit lists active privileged accounts ``hl``,
    ``sirkku`` and ``tuula`` whose passwords are absent from the vault. The
    inactive staff account ``anja`` still has its staff flag. The deployment
    data named ``kasvimuseo_admin_passwords`` can rotate the passwords, and the
    maintenance playbook now checks both account conditions before rotation.
:Depends on: (none)
:Blocks: (none)
:Related: 050 -- the existing admin password rotation
    049 -- the security maintenance window that can apply the rotation
:Decision: Keep ``hl``, ``sirkku`` and ``tuula`` active, and rotate each through
    the encrypted vault. Remove ``anja``'s stale staff privilege during the
    controlled production maintenance window. The playbook must audit active
    privileged accounts before it rotates any password.
:Resolution: ``2405e8a`` adds the pre-rotation account gates. The production
    owner must add approved passwords to the encrypted host variables and apply
    the ``anja`` account decision during the maintenance window. No password is
    stored in this repository.

Problem
-------

The project could not verify or rotate every privileged production account.
Unknown passwords and stale staff flags increase the cost of a compromise.
The maintenance playbook now stops before rotation when an active privileged
account is outside the vault.

What remains
------------

The decision keeps the three active accounts and removes ``anja``'s staff flag.
The deployment owner must add approved passwords to the vault and rotate them.
The owner must apply the account decision and record the result without writing
passwords in this repository.
