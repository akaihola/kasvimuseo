===============================================================================
Issue 074: Production runs a newer Django than the pin
===============================================================================

:Status: Open
:Severity: High
:Area: deployment / dependencies
:Reported: 2026-08-26
:Source: Maintenance window report in ``docs/issues/incoming.rst``
:Evidence: ``requirements/production.txt`` pins ``django==1.11.29``. The
    production traceback uses ``django/contrib/auth/base_user.py``, which does
    not exist in the checked 1.8.19 wheel. A new password hash uses 36 000
    PBKDF2 iterations, while Django 1.8 writes 20 000. The exact deployed
    version still needs a ``pip2 freeze`` reading.
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- Stage 9 pins Django 1.11.29 and the upgrade depends on a
    known starting version
    068 -- restored passwords depend on the Django password hasher
:Decision: undecided
:Resolution: (none yet)

Problem
-------

Production does not match the Django version that the repository declares.
The drift can change password hashing, migrations and supported Grappelli code.

What remains
------------

The deployment owner must record the installed Django version and its package
set. The owner must then choose whether to restore the pin or update the
repository after checking migrations and dependency support.
