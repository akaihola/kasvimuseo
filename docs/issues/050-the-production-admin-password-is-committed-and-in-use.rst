==============================================================
Issue 050: A production admin password is committed and in use
==============================================================

:Status: Open
:Severity: High
:Area: security / deployment
:Reported: 2026-07-31
:Source: Issue 017, while deleting the browser suite that carried it
:Evidence: (none -- nothing this repository can test says whether a password on
    another machine has been changed)
:Depends on: (none)
:Blocks: (none)
:Related: 025 -- the same shape: the repository half is done here, the act that
    ends the disclosure is somewhere else
    049 -- the other half of 025, waiting on the same kind of decision
    017 -- the file this was found in, and which deleted it
:Decision: undecided -- the password has to be changed on the running server,
    and when to spend the logout is the maintainer's call. Filed separately
    from 017 rather than inside it, on 025 and 049's precedent: 017 could take
    the secret out of the tracked files and nothing more.
:Resolution: (none yet)

Problem
=======

``integration_tests/tests/conftest.py`` logged the browser suite into the admin
with a username and a password written into the file::

    sb.update_text('#id_username', 'akaihola')
    sb.update_text('#id_password', '123')

It is not a placeholder. Against the production dump in
``.dev/backups/production.sql``, PBKDF2-SHA256 of ``123`` with that row's own
salt and its 10 000 iterations reproduces the stored hash for
``auth_user`` id 1 exactly:

======================= =========================================================
 Account                ``akaihola``, id 1, ``is_staff``, ``is_active``,
                        ``is_superuser``
 Stored hash            ``pbkdf2_sha256$10000$xNbFfRLV70e3$m68d3K0kWUSLqR9…``
 ``pbkdf2('123', …)``   the same string
 Last login in the dump 2025-04-08
======================= =========================================================

So the repository has been publishing a working superuser login for the
production admin, on a site reachable from the internet, since commit 529011d
("Start implementing Selenium tests", 2020-01-17).

Impact
======

Anyone who has read this repository -- it has a public GitHub mirror -- can sign
in to the production admin as a superuser: every plant record, every photo, and
the ``auth`` tables. It is a larger exposure than 025's, because it needs no
access to the server and no understanding of Django to use, and it is live until
somebody changes the password.

What has been done here
=======================

Issue 017 deleted ``integration_tests/``, so the password is no longer in any
tracked file. **That remediates nothing by itself** -- exactly as 025's file
says of the ``SECRET_KEY``. It is still in the history, in every clone and on
both remotes, and it is still the password the account uses.

What is left, and it is not in this repository
==============================================

1. Change that account's password on the production server. One command::

       $ ansible ... # or: manage.py changepassword akaihola

2. Look at the other four accounts in the same table while there. Three of them
   are staff, one is a second superuser, and none of their passwords is known to
   be strong; this one was three digits.
3. Decide whether to treat the disclosure as exploited. Nothing in the dump says
   whether the login was ever used from outside, and the admin's ``LogEntry``
   table is the only record of what would have been done with it.

The cost is one round of logouts for that account, and it does not depend on
049 or on anything else in this register.
