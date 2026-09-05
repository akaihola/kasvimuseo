===============================================================================
Issue 074: Production runs a newer Django than the pin
===============================================================================

:Status: Fixed
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
:Decision: Keep Django at ``1.11.29`` and make the Ansible code deployment
    reinstall the application and its exact runtime dependencies. The
    repository's Stage 9 pin remains the supported Python 2.7 staging point.
:Resolution: fa6e1ac -- ``ansible/install.yaml`` now passes ``--upgrade
    --force-reinstall`` to pip2 for the application install. The documented
    ``-t code`` deployment repairs an existing newer Django before traffic
    resumes. Django 1.11.29 adds no application migration.

Problem
-------

Production does not match the Django version that the repository declares.
The drift can change password hashing, migrations and supported Grappelli code.

Result
------

The production deployment now restores the repository pin through the
documented ``ansible-playbook -t code ansible/install.yaml`` command. The
runtime lock remains ``django==1.11.29``. This correction alone needs no
database migration.
