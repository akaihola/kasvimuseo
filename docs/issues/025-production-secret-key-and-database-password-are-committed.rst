====================================================================
Issue 025: Production SECRET_KEY and database password are committed
====================================================================

:Status: Fixed
:Severity: High
:Area: security / settings
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``kasvimuseo/tests/test_settings_secrets.py`` -- added with the fix; it pins that ``secret_from_env`` has no default and names the missing variable. Nothing pinned the old behaviour, since a committed constant is not something a test can catch.
:Depends on: (none)
:Blocks: 049 -- deploying the rotated values needs settings that read them from the environment, which is what this issue did
:Related: 026 -- the same file, and the same question of what the server carries that the repository does not
:Decision: Option 2 in this repository, option 3 for the history, and option 1 handed on. The settings read both values from the environment (``KASVIMUSEO_SECRET_KEY``, ``KASVIMUSEO_DB_PASSWORD``) with no default, and Ansible supplies them from the vault the repository already had (option 2). The history is left alone (option 3): rewriting it un-discloses nothing, and rotation makes what is in it worthless. Rotation itself (option 1) is half done -- the maintainer has generated new values and put them in the vault -- and the deploy that makes them the ones in use is **issue 049**, which waits on agreeing the timing with the customer.
:Resolution: Commit a58a697 moved both values out of every tracked file and into the environment, b8a380d recorded that half; no tracked file holds either value. That is all of this issue that the repository can do. It did not end the disclosure -- see 049, which is the step that does.

.. warning::

   **``Fixed`` here means the repository, not the disclosure.** No tracked file
   holds either value any more, and the maintainer has rotated both into the
   vault -- but the server has not been updated, so the running application is
   still signing with the key that is in this repository's history. Anyone who
   has ever had a clone can still forge an admin session. :doc:`049
   <049-production-still-runs-the-old-secret-key-and-database-password>` is that
   deploy, and it is open.

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

``fabfile.py`` -- **deleted since**
    The Kajala password it held was made to read from the environment too: the
    file was superseded by Ansible but still tracked, so it could not keep the
    value. Issue 032 has since deleted it, having checked first that this was
    not the last copy of anything -- the same environment variable, with the
    same explanation, is read in ``ylaneenkasvit/kajala_settings.py``, which is
    where the Kajala database password actually reaches the application.

Measured, in the container: the suite passes (357 tests, three of them the new
ones for ``secret_from_env``); with both variables
set the site starts under ``ylaneenkasvit_settings`` and ``admin`` logs into
``/admin/`` and gets a signed session cookie; with ``KASVIMUSEO_SECRET_KEY``
unset the import fails with ``ImproperlyConfigured: KASVIMUSEO_SECRET_KEY is
not set...`` rather than starting.

Rotation, which is not this issue
=================================

The repository change above remediated nothing on its own: it stopped the
repository from being where the secrets live, and it made a deployment that has
not been handed them fail rather than start with a known key. Only changing the
values ends the disclosure, and only a deploy makes a changed value the one in
use.

The maintainer generated new values on 2026-07-30 and put them in
``ansible/host_vars/<host>`` as ``kasvimuseo_secret_key`` and
``kasvimuseo_db_password``. Recorded on their word: nothing in this repository
can observe the vault or the server, which is the same reason the repository half
could be verified here and this half cannot.

**The new values are not in use.** uWSGI keeps the environment it started with,
so until the playbook runs, the application signs with the old key and connects
with the old password, and the disclosure described under "Impact" above is
exactly as it was when this issue was filed. That deploy is
:doc:`049 <049-production-still-runs-the-old-secret-key-and-database-password>`:
it is a separate issue because it is a separate act, on a machine this repository
cannot reach, and because its timing has to be agreed with the customer -- a new
``SECRET_KEY`` logs everybody out once and kills outstanding password-reset
links, which is the entire cost but is not the maintainer's alone to spend.

Option 3 stands either way: the history is left as it is. Rewriting it would not
un-disclose anything, and once 049 lands, what is in it is worthless.
