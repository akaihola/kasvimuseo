========================================================
Issue 067: ``db bootstrap`` ignores the dump it is given
========================================================

:Status: Fixed
:Severity: Medium
:Area: development tooling
:Reported: 2026-08-03
:Source: The maintainer, who could no longer log in as ``akaihola`` on a local
    server and asked where the new password was and whether the production dump
    could be turned into one whose logins are known
:Evidence: The reproduction is the reported command itself, and it needs no
    test to be unambiguous: ``dev/kasvimuseo db bootstrap
    .dev/backups/production.sql`` exits 0, prints a full migration run, and
    leaves ``SELECT count(*) FROM auth_user`` at ``0``. There is no automated
    test here because nothing in this repository tests ``dev/kasvimuseo`` --
    the suite is Django tests inside the container and the script is what
    starts the container -- so both halves of the fix were verified by running
    them, and the transcripts are in "Verification"
:Depends on: (none) -- one guard in a ``case`` arm and one new command, both
    in ``dev/kasvimuseo``
:Blocks: (none)
:Related: 050 -- the account and the password. That issue is why the question
    "where do I get the new password" is worth answering carefully, and why
    ``db development`` is worth having: the answer today is that nothing was
    changed, and the answer after 050 is finally acted on will be that nobody
    developing here can know it
    055 -- the other defect found in a bootstrapped database, and the same
    shape at one remove: a database this repository builds is missing rows that
    the production dump has, and nothing says so at the time
    025 -- the rule these credentials follow: a real one is never in a tracked
    file, and a development one is a named default that says what it is
:Decision: Both halves as reported. The maintainer's message is itself the
    ruling on the second -- "could we make a ``development.sql`` version from
    ``production.sql`` so ``akaihola`` is readily logged in" is a request for
    work, not a question about a design -- and the first needs no ruling under
    this page's own first ordering rule: the script is plainly not doing what
    it was written to do, and refusing an argument it cannot honour is not a
    product decision. Two choices inside the second half were made here rather
    than asked about, and both are argued below: every account's password is
    replaced rather than ``akaihola``'s alone, and the hash is made by the
    application's own hasher in the container rather than by this script
:Resolution: 9fa70bf -- the guard in ``db bootstrap``'s ``case`` arm, the new
    ``db_development`` beside ``db_restore``, and the two paragraphs of
    ``README.rst`` that document both. Nothing outside ``dev/kasvimuseo`` and
    the documentation changed, and 050 is untouched: the password on the server
    is still the one it describes, and this makes that fact survivable here
    rather than ending it

Problem
=======

The command that was run::

    $ dev/kasvimuseo db bootstrap ~/prg/kasvimuseo/.dev/backups/production.sql

``db bootstrap`` takes no arguments. It builds an **empty** database from the
migrations, for working with no production data at all; the path was accepted,
dropped, and never mentioned again. What the terminal showed was a complete,
successful migration run and an exit status of 0, and what was in the database
afterwards was every table the application needs and not one row of the dump::

    $ dev/kasvimuseo db psql -tAc "SELECT count(*) FROM auth_user"
    0

So the next thing that happened was a login screen that rejected the right
password, because there was no account to reject it for. Nothing in the output
of either command said so.

Impact
======

A developer who reaches for the wrong one of two adjacent commands gets a
plausible, empty database and a login failure, and the failure looks like a
credentials problem -- which sends them looking for a password that was never
wrong. The cost is entirely in the wrong diagnosis: the report this issue came
from asks where the new password can be found, and there is no new password.
Nothing about production is affected; ``dev/kasvimuseo`` runs nowhere else.

Where the password can be got, since that was the question
==========================================================

**It was not changed, and it is still** ``123``. The ``auth_user`` row for
``akaihola`` in ``.dev/backups/production.sql`` carries the same hash
:doc:`050 <050-the-production-admin-password-is-committed-and-in-use>` recorded,
and PBKDF2-SHA256 of ``123`` with that row's salt and its 10 000 iterations
reproduces it exactly -- recomputed while writing this, not copied from 050.
The dump is recent (the newest ``last_login`` in it is 2026-07-27), so this is
not a stale file: as of that dump, the disclosed password is still live on
production, and 050 is still open for exactly that reason.

Had it been changed, the answer would be **nowhere**. A dump stores a one-way
hash, so no dump can be made to give up a password; the only routes are to set
a new one on the running server, or to set one locally on the restored copy,
which is what the second half of this fix does for every account at once. Both
are worth writing down, because 050's remaining work is a password change on
production, and the first ``db fetch`` after it will produce a dump that nobody
here can sign into.

The fix
=======

Two changes, both in ``dev/kasvimuseo``.

**1. ``db bootstrap`` refuses an argument.** It cannot honour one, so it says
so and names the command that can::

    $ dev/kasvimuseo db bootstrap .dev/backups/production.sql
    db bootstrap takes no arguments: it builds an empty database from
    the migrations. To load the dump instead:
      dev/kasvimuseo db restore .dev/backups/production.sql

**2. ``db development`` writes the dump the maintainer asked for.** It reads
``.dev/backups/production.sql`` and writes ``.dev/backups/development.sql``
beside it, identical except that every ``auth_user`` password is one the person
restoring it knows::

    $ dev/kasvimuseo db development
    Replaced 5 passwords.
    Wrote .dev/backups/development.sql. Every account in it now has the
    password 'development':
      dev/kasvimuseo db restore .dev/backups/development.sql

The password is ``development``, the same named default and for the same reason
as the local database password and the development ``SECRET_KEY`` beside it in
the script (issue 025); ``KASVIMUSEO_DEV_PASSWORD`` overrides it. Both paths
and the file names are defaults, so a dump taken with Ansible can be named on
the command line instead.

Three things about it were decided rather than assumed:

*Every account, not only* ``akaihola``. The narrow version would leave four
production password hashes in the file that then gets restored, opened in
``psql``, and copied between machines -- and one of those hashes is three
digits. Rewriting all five makes the derived dump carry no production
credential at all, which is a second reason to prefer it over the original
even once 050's change lands. Nothing else is touched: the names, the
addresses and every plant record are still the real ones, because this is a
development database rather than an anonymised one, and pretending otherwise
would be worse than not claiming it.

*The hash comes from the application*, not from this script's idea of the
format. ``db development`` runs ``make_password`` in the container, so the
algorithm and the iteration count are whichever Django is installed -- 12 000
iterations today against the dump's 10 000, which is what Django's own upgrade
of the default looks like. A literal written into a shell script would be a
second, silent opinion about a format the upgrade plan is going to move.

*The column is found rather than counted.* The dump names its columns in the
``COPY`` header, so the ``awk`` pass reads ``password``'s position from there
and fails loudly if there is none, rather than trusting field 6 to stay field
6.

Verification
============

Both halves were run. The guard, and the empty database it now prevents::

    $ dev/kasvimuseo db bootstrap .dev/backups/production.sql; echo "exit=$?"
    db bootstrap takes no arguments: ...
    exit=1

The derived dump differs from the production one in five lines, all of them
``auth_user`` rows, and in nothing else -- ``diff`` reports ``1592,1596c1592,1596``
and no other hunk. Restored and served, the reported login works::

    $ dev/kasvimuseo db development
    $ dev/kasvimuseo db restore .dev/backups/development.sql
    $ dev/kasvimuseo db upgrade-photologue     # pre-Stage-2 dump, as documented
    $ KASVIMUSEO_PORT=8077 dev/kasvimuseo app run

POSTing ``akaihola`` and ``development`` to ``/admin/`` with the rendered CSRF
token answers ``302`` to ``/admin/``, and the page that follows carries the
name ``akaihola`` -- an authenticated session, not the login form again.

The two failure paths were run as well: a file with no ``auth_user`` block is
refused and no half-written output is left behind, and a source path that does
not exist is refused with the ``db fetch`` that would produce one.

The documentation build was run, and ``README.rst`` -- which is
:doc:`../development`, included -- now documents ``db development`` where it
documents ``db restore``, and says that ``db bootstrap`` takes no dump.
