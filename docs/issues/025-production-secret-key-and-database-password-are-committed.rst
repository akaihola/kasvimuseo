====================================================================
Issue 025: Production SECRET_KEY and database password are committed
====================================================================

:Status: Accepted
:Severity: High
:Area: security / settings
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``kasvimuseo/tests/test_settings_secrets.py`` -- added with the fix; it pins that ``secret_from_env`` has no default and names the missing variable. Nothing pinned the old behaviour, since a committed constant is not something a test can catch.
:Depends on: (none)
:Blocks: (none)
:Related: 026 -- the same file, and the same question of what the server carries that the repository does not
:Decision: Option 2 and option 3, not yet option 1. The settings read both values from the environment (``KASVIMUSEO_SECRET_KEY``, ``KASVIMUSEO_DB_PASSWORD``) with no default, and Ansible supplies them from the existing vault; the history is left alone. Rotation -- option 1, and the only thing that ends the disclosure -- is the maintainer's to perform on the server and is *not* done. ``Status`` therefore stays ``Accepted`` rather than ``Fixed``, so this issue stays in the queue for that half.
:Resolution: Repository half only, in commit f097898: no tracked file holds either value any more. The disclosure itself is unresolved.

.. warning::

   **This issue is half fixed, and the half that is still open is the one that
   matters.** The repository no longer carries the two values, but the values
   are unchanged and remain in the git history, so anyone who has ever had a
   clone can still forge an admin session and still knows the database
   password. Nothing here rotated anything. Until the maintainer generates a
   new ``SECRET_KEY`` and a new database password and puts them in the vault,
   this issue's *impact* is exactly what it was when it was filed.

   The change also means the deployment **fails until those two variables are
   set on the server** -- deliberately, in preference to starting with a known
   key. See `What is left to do`_.

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

What was done
=============

Option 2, following the environment-variable convention the repository already
used for the database connection (``KASVIMUSEO_DB_HOST`` and friends in
``local_settings.development.py``, ``KASVIMUSEO_DEBUG`` in
``common_settings.py``). Two variables: ``KASVIMUSEO_SECRET_KEY`` and
``KASVIMUSEO_DB_PASSWORD``.

Neither has a default, and that is the point. ``common_settings.secret_from_env``
raises ``ImproperlyConfigured`` naming the missing variable, so a deployment
that forgets one stops rather than coming up signing session cookies,
password-reset tokens and CSRF tokens with a value that is in this repository's
history. Where it was plumbed:

``ylaneenkasvit/common_settings.py``
    ``secret_from_env(name)`` -- the one place that decides what a missing
    secret means.

``ylaneenkasvit/ylaneenkasvit_settings.py``, ``ylaneenkasvit/kajala_settings.py``
    ``SECRET_KEY`` and the database ``PASSWORD`` read through it. The literals
    are gone from both.

``ylaneenkasvit/test_settings.py``
    ``SECRET_KEY = 'test'`` stays: the suite signs nothing that outlives it, so
    it supplies its own literal rather than needing a variable set. The
    database password's ``os.environ.get(...)`` default -- which was the
    production password -- is now an empty string, since the throwaway
    development cluster trusts local connections.

``dev/kasvimuseo``
    Passes ``KASVIMUSEO_SECRET_KEY`` into the app container beside the database
    variables it already passed, defaulting to an obviously-not-production
    development key, and its ``KASVIMUSEO_DB_PASSWORD`` default is no longer
    production's. ``db fetch`` is the one command that authenticates against
    production, so it now refuses to run unless the real password is given to
    it explicitly.

``ansible/install.yaml``, ``ansible/vars/main.yml``, ``ansible/roles/akaihola.uwsgi``
    The values come from the vault file the repository already has,
    ``ansible/host_vars/<host>`` (decrypted by ``ansible/get-vault-password.sh``),
    as ``kasvimuseo_secret_key`` and ``kasvimuseo_db_password``. The playbook
    asserts both are defined before it installs anything; the uWSGI template
    writes them into ``/home/kasvimuseo/uwsgi.ini`` as ``env =`` lines, mode
    ``0600`` and ``no_log``, which is how the running application gets them; and
    ``collectstatic`` gets them in its environment, since importing the
    settings now needs them. ``postgresql_users`` takes the password from the
    same variable instead of the plain-text one it held.

``fabfile.py``
    The Kajala password it held is read from the environment too. The file is
    superseded by Ansible (issue 032) but is still tracked, so it could not
    keep the value.

Measured, in the container: the suite passes (340 tests, three of them the new
ones for ``secret_from_env``); with both variables
set the site starts under ``ylaneenkasvit_settings`` and ``admin`` logs into
``/admin/`` and gets a signed session cookie; with ``KASVIMUSEO_SECRET_KEY``
unset the import fails with ``ImproperlyConfigured: KASVIMUSEO_SECRET_KEY is
not set...`` rather than starting.

What is left to do
==================

Two things, both on the server and neither doable from the repository:

1. **Set the variables.** Add ``kasvimuseo_secret_key`` and
   ``kasvimuseo_db_password`` to ``ansible/host_vars/<host>`` with
   ``ansible-vault edit`` and run ``ansible-playbook ansible/install.yaml``.
   Until then the deployment fails -- the playbook stops at the assertion, and
   an application started by hand raises ``ImproperlyConfigured``. That is the
   intended failure mode, but it does mean the next deploy needs this done
   first.

2. **Rotate both** (option 1), which is the only step that actually ends the
   disclosure. Generate a new ``SECRET_KEY``, change the PostgreSQL user's
   password, put both in the vault. The cost is one round of logouts and any
   outstanding password-reset links going dead; that is the entire cost. Nobody
   needs to touch the code for it, which is the reason to do option 2 first.

Option 3 stands: the history is left as it is. Rewriting it would not
un-disclose anything, and rotation makes what is in it worthless.
