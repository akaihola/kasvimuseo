=============================================================================
Issue 049: Production still runs the old SECRET_KEY and database password
=============================================================================

:Status: Accepted
:Severity: High
:Area: deployment / security
:Reported: 2026-07-30
:Source: Maintainer, on reading the repository half of 025
:Evidence: (none) -- nothing in this repository can observe the server's
    environment, which is the whole reason this is a separate issue from 025
:Depends on: 025 -- the deployment can only supply these values from the vault
    because the settings now read them from the environment; that is what 025
    did, and it is ``Fixed``
:Blocks: (none)
:Related: 025 -- where the values came out of the tracked files, and where the
    disclosure this issue ends is described
    026 -- the other thing only a look at the running server can settle
:Decision: undecided -- **not** whether to do it, which is agreed, but when.
    The maintainer wants it agreed with the customer first, because the visible
    cost lands on them: everybody logged in is logged out once, outstanding
    password-reset links stop working, and the site is briefly down while uWSGI
    restarts. Ruling this means picking a time, not choosing between options.
:Resolution: (none yet)

Problem
=======

Issue 025 has two halves and only the repository one is done. The tracked
settings no longer contain the production ``SECRET_KEY`` or the database
password, both are read from the environment, and the maintainer has generated
new values and put them in the Ansible Vault file for the host.

The server has not been updated. uWSGI keeps the environment it started with, so
the running application is still signing session cookies, password-reset tokens,
``django.core.signing`` payloads and CSRF tokens with the key that is in this
repository's history, and still connecting to PostgreSQL with the password that
is in it. The new values sit in the vault, unused.

Impact
======

Exactly the impact 025 described, unchanged and for as long as this is open:
anybody who has ever had a clone of this repository can forge a session cookie
for any account, including a superuser. Rotating the values in the vault did not
change that -- deploying them is what changes it.

That is worth stating plainly because the repository now *looks* remediated. A
reader who greps the tree for the old key finds nothing and can reasonably
conclude the problem is gone. It is not: it moved from the repository to the
gap between the vault and the running process.

What it takes
=============

One playbook run, and the ordering inside it matters::

    $ ansible-playbook ansible/install.yaml

The two tasks that carry these values have to land together. The database role
sets the PostgreSQL user's password from ``kasvimuseo_db_password``, and the
uWSGI role writes both values into ``/home/kasvimuseo/uwsgi.ini`` and restarts
the service when that file changes. Run only ``-t database`` and PostgreSQL has
the new password while the running application still has the old one in its
environment; run only ``-t web`` and the application gets a password PostgreSQL
does not have yet. Either half alone breaks the site until the other one runs.
A full run, or ``-t database,web``, does both.

The assertion added by 025 fails the run before anything is installed if either
value is missing from the vault, so a forgotten variable stops the deploy rather
than the site.

The playbook that does it exists now
====================================

``ansible/secure-production.yaml`` is the maintenance window as a playbook: it
imports ``install.yaml`` whole -- so this issue's deploy is exactly the run
described above, not a reimplementation of it -- and then carries out the two
other server-side acts that are open, 050's password rotation and 051's
deletion, in the one order that is safe. ``README.rst``, under "The security
maintenance window", is the runbook: the command, the downtime, what the
customer sees, and what is checked afterwards. Its last play asserts this
issue's own post-conditions on the server -- that ``uwsgi.ini`` carries the
values the vault holds, and that uWSGI *started after* that file was written,
which is what distinguishes a process signing with the new key from one still
signing with the old.

This changes nothing about the state of the disclosure, which is why ``Status``
still says ``Accepted``. What was missing was never the knowledge of what to
type; it was the decision this issue's ``Decision`` field names, and that is
still the customer's to give. The mechanism is ready, and the disclosure is live
until somebody runs it.

What to expect afterwards
=========================

All three of these are the intended consequences of a new ``SECRET_KEY``, not
signs that something went wrong:

* Every session is invalidated, so everybody logged in at the moment of the
  restart is logged out once and logs back in normally.
* Password-reset links issued before the deploy stop working. Requesting a new
  one works.
* The site is down for as long as the uWSGI restart takes.

This is the entire cost, and it is why the timing is the customer's to agree
rather than something to slip into an unrelated deploy.

How to tell it worked
=====================

From the browser: log in to the admin. A session cookie signed with the old key
is no longer accepted, so an already-open session asks for the password again --
that is the observable evidence the key changed. From the server: the
``KASVIMUSEO_SECRET_KEY`` line in ``/home/kasvimuseo/uwsgi.ini`` matches the
vault, and the uWSGI process started after the file was written
(``systemctl show -p ActiveEnterTimestamp ylaneenkasvit-wsgi``).

Do not paste either value into this issue, a commit message or a ticket when
recording that it is done. Naming the commit that deployed it is enough, and is
what ``Resolution`` is for.
