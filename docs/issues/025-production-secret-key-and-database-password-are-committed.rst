====================================================================
Issue 025: Production SECRET_KEY and database password are committed
====================================================================

:Status: Open
:Severity: High
:Area: security / settings
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``ylaneenkasvit/ylaneenkasvit_settings.py`` contains the live production
``SECRET_KEY`` and the production database password in plain text, tracked in
git. The same password appears again in ``ylaneenkasvit/test_settings.py`` as a
default.

Both are in the repository's history, so deleting them from the working tree
does not remove them -- anyone with a clone, at any point in the past, has them.

What Django's ``SECRET_KEY`` protects here: session cookie signing, the
password-reset token generator, ``django.core.signing`` and CSRF token
generation. Disclosure allows forging session cookies and password-reset links
for any account, including superusers.

Impact
======

Anyone who has ever had read access to this repository can forge an admin
session. Whether that matters depends on who that is -- which is a question for
the maintainer, not something this analysis can answer, hence High rather than
a judgement call about exploitation.

The database password matters less if PostgreSQL is only reachable over a local
socket, which the ``'HOST': '/var/run/postgresql'`` default suggests.

Options
=======

1. **Rotate both.** A new ``SECRET_KEY`` invalidates all existing sessions --
   users get logged out once -- and all outstanding password-reset links. That
   is the entire cost.
2. **Move them out of the file**, reading from the environment with
   ``os.environ['...']``. The deployment already passes environment variables
   into the container (``dev/kasvimuseo`` does this for the database), and
   ``ansible/install.yaml`` is the natural place to set them in production.
3. Leave the history alone. Rewriting it is disruptive and buys nothing once
   the secrets are rotated.

This is unrelated to the upgrade, but it is in the same file the upgrade will
touch repeatedly, so it is worth deciding on now.
