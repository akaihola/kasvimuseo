==============================================================
Issue 050: A production admin password is committed and in use
==============================================================

:Status: Fixed
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
:Decision: rotate ``akaihola`` in the same customer-agreed window as 049; it
    ran on 2026-08-26. On this issue's third point -- whether to treat the
    disclosure as exploited -- ruled on the only record there is, read by the
    audit below: the account has no admin action after 2025-04-08, and
    ``LogEntry`` does not record logins or their origin. So the ruling is "no
    observed misuse, and a silent sign-in cannot be excluded"; the rotation
    ends the question rather than answers it. Filed separately from 017 on
    025 and 049's precedent: 017 could take the secret out of the tracked
    files and nothing more.
:Resolution: rotated in the 2026-08-26 window by Play 2 of
    ``ansible/secure-production.yaml`` -- rerun with the fix in 7ea4dc0,
    after the first run died in ``AppRegistryNotReady`` before it changed
    anything. The report named ``akaihola`` under ``changed`` and nothing
    under ``missing``; the verify play's dry run then confirmed every
    vaulted account holds the vaulted password; and the maintainer confirmed
    in the browser that ``123`` no longer signs in. The audit's reading is
    the last section below

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

The playbook that does it exists now
====================================

``ansible/secure-production.yaml``, described in ``README.rst`` under "The
security maintenance window". Point 1 above is a task in it, and the two
sentences worth reading here are about what it does and does not settle:

* ``manage.py changepassword`` is not what it uses, because that command
  prompts and cannot be driven from a playbook. It feeds a short script to the
  server's Python on **standard input**, so no password reaches an argument
  list, a process environment or the play's output, and the new values come
  from the vault -- ``kasvimuseo_admin_passwords``, a mapping of user name to
  new password, in the encrypted ``host_vars`` file. None of them is in a
  tracked file. It is idempotent: an account that already has the vaulted
  password is left alone, so a second run rotates nothing.
* **Point 2, the other four accounts: covered as far as a playbook can cover
  them.** Every account the vault names is rotated, so adding the other four to
  ``kasvimuseo_admin_passwords`` is all it takes to include them -- but
  choosing whether they should keep an account at all is a judgement, not a
  task, so the playbook does not decide it. What it does instead is print every
  account in ``auth_user`` with its hash algorithm, its iteration count, its
  last login and its admin activity, and name the privileged ones it is *not*
  rotating. That is the "look at them while there" this issue asked for, in a
  form that does not go stale.
* **Point 3, whether to treat the disclosure as exploited: not covered, and it
  cannot be.** The same report prints each account's ``LogEntry`` count and the
  dates of its first and last admin action, because that table is the only
  record there is. Reading it and ruling is a person's job; ``Decision`` is
  still ``undecided`` for exactly that reason.

That described the state before the window. The playbook ran on 2026-08-26;
``Resolution`` records what it did, and the audit it printed reads as follows.

The audit, 2026-08-26
=====================

Play 2 read every ``auth_user`` row on the production server after the
rotation. The saved play output is the full record; these are the facts it
settles.

===================== =========== ======= ============ ==================
 Account               Privilege   Active  Last login   Last admin action
===================== =========== ======= ============ ==================
 ``akaihola`` (id 1)   superuser   yes     2026-08-14   2025-04-08
 ``hl`` (id 2)         staff       yes     2026-08-10   2026-08-06
 ``anja`` (id 3)       staff       no      2023-08-06   2023-08-06
 ``sirkku`` (id 4)     superuser   yes     2026-06-15   2022-06-14
 ``tuula`` (id 5)      staff       yes     2025-04-08   never
===================== =========== ======= ============ ==================

* The rotation changed ``akaihola`` and nothing else, which is exactly what
  the vault covers. The three other active privileged accounts keep their
  old passwords -- ``docs/issues/incoming.rst`` carries that report onward.
* Every hash is PBKDF2-SHA256. The four untouched ones sit at 10 000
  iterations, the strength of the Django that last wrote them.
* ``akaihola`` has 120 admin actions, the last on 2025-04-08. Between the
  disclosure (2020) and the rotation, nothing in the admin's own history was
  done through the account after that date. Logins leave no trace of their
  origin, which is as far as this record can see.
