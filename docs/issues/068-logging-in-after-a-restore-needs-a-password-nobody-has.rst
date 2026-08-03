==============================================================================
Issue 068: Logging in after a restore needs a password nobody has
==============================================================================

:Status: Fixed
:Severity: Low
:Area: development workflow / authentication
:Reported: 2026-08-03
:Source: Asked by the maintainer as work: what is the shortest shell command
    that logs ``akaihola`` into the development site after a database restore,
    so that opening ``localhost:8000`` lands on an admin that is already
    logged in -- is there a management command, a short Django API call, or
    another trick? The friction behind the question is older than the
    question: every ``db restore`` has ended in the same detour since the
    local cluster existed
:Evidence: (none) before this change -- there was nothing to pin, since the
    missing thing was a route rather than a behaviour.
    ``kasvimuseo/tests/test_dev_login.py`` is the evidence now, and half of it
    is about the route *not* existing: the URLconf carries it only with
    ``DEV_LOGIN`` on, and the view refuses even when something reaches it
    anyway
:Depends on: (none)
:Blocks: (none)
:Related: 067, ``db bootstrap`` ignores the dump it is given -- the closest
    neighbour, and it narrowed this issue rather than closing it. Its fix added
    ``db development``, which rewrites every password in a dump to a known one,
    so a derived dump can be signed into; what is left after it is the login
    form itself, and a dump restored as it came, which is what this issue is
    about. Its own reason for existing survives too: those hashes should stop
    being circulated at all (050), and a route that needs no password does not
    circulate one
    049 and 050 -- why the restored passwords are unusable here. 050 is
    the one committed password that does work, and it is production's admin
    account, which is precisely the credential this repository should stop
    circulating rather than type into a development form
    051 -- production ran with ``DEBUG`` on behind an untracked
    ``local_settings.py``. That is the reason this gate is its own environment
    variable and not a reading of ``settings.DEBUG``: a gate that trusts
    ``DEBUG`` would have been open on that server
    052 -- the label editor's save is staff-only, so working on it means being
    logged in, which is the same detour from the other end
    026 -- the same mechanism, an environment variable read in
    ``common_settings`` and supplied by ``dev/kasvimuseo`` for development and
    by ``uwsgi.ini`` for production
:Decision: Ruled by the ask, between the three answers it named. (1) A
    management command. Django ships none, and one cannot be the whole answer:
    what logs a browser in is a ``sessionid`` cookie in that browser, and a
    process in a container cannot put one there. It could create the session
    row and print its key, but something still has to carry the key across, so
    the command would be half a mechanism with a URL bolted to it. (2) A short
    Django API call -- ``django.contrib.auth.login`` needs a request, and
    ``SessionStore`` from a shell has the same cookie problem; what is short
    from a shell is not the API but the address bar. (3) A URL, which is what
    this is: ``/dev-login/<username>/``, one ``xdg-open`` away, no password and
    no form. The cost is a password-free admin login for anyone who can reach
    the port, so it is gated on ``KASVIMUSEO_DEV_LOGIN``, set by
    ``dev/kasvimuseo`` and by nothing else, and turned off with the variable
    emptied. That gate is deliberately not ``DEBUG`` (see 051) and deliberately
    not a check on the client address: the development browser is often on
    another machine, which is what 044 is about, so a loopback-only rule would
    refuse exactly the case that needs it most
:Resolution: f44adf0

Problem
=======

``dev/kasvimuseo db restore`` loads production's dump into the local database,
which is what makes a development checkout useful: the label editor, the admin
change forms and the reports all behave differently on 311 observations than on
a fixture. The dump is the whole database, so it brings two tables that decide
who the browser is.

``auth_user`` becomes production's. The hashes in it are production's hashes,
and this repository is not supposed to be able to turn them back into
passwords: issue 049 is the disclosed credentials that have not been rotated,
and issue 050 is the one admin password that *is* known here, committed in
2020 and still live. Typing that one into a development login form is not a
workaround, it is the practice 050 exists to end.

``django_session`` becomes production's too. The browser's ``sessionid`` cookie
survives the restore -- a cookie is not in the database -- but the row it names
does not, so the session is anonymous on the next request. Every restore
therefore logs the developer out, and the way back in was::

    $ dev/kasvimuseo app manage changepassword akaihola
    ... twice, at a prompt, in a container ...
    ... then the login form, in the browser ...

for a server whose database is a throwaway copy, whose ``ALLOWED_HOSTS`` is
``*`` and whose secret key is the string ``development-only-not-a-production-key``.

Issue 067 -- ``db bootstrap`` ignores the dump it is given -- has since made
that first line unnecessary for anybody who takes the extra step it added:
``db development`` writes a copy of the dump with every account's password set
to ``development``, and restoring that copy leaves a database that can be
signed into. It is the better answer to the "nobody has it" half, and it
deliberately does not touch the other two. A dump restored as it came -- which
is what happens whenever the derived copy was not made, or the database came
from somewhere else -- still has no usable password; and either way the browser
still meets the login form after every restore, having been logged out by the
session table that came with the dump.

What Django offers
==================

Nothing that does this. ``createsuperuser`` and ``changepassword`` are the two
auth commands, and both end at the same login form. ``django-extensions`` --
which is installed here, for ``runserver_plus`` and ``shell_plus`` -- adds
``set_fake_passwords``, which sets every account's password to a known string;
that removes the "nobody has it" half of the problem and leaves the form. This
project's own ``db development`` (issue 067) is the same shape and a better
version of it: it rewrites the passwords in the dump rather than in a database,
so no hash of production's is restored at all. All three stop in front of the
form.

The Python API is no shorter, and for a reason that is not about the API.
``django.contrib.auth.login(request, user)`` writes the two auth keys into
``request.session``; ``SessionStore`` can write the same keys from a shell
without any request at all. Either way the session ends up in the database
under a key, and the browser is logged in only if it sends that key as its
``sessionid`` cookie. A management command, a ``manage.py shell`` heredoc and a
``psql`` insert all stop one step short of the browser, and the step they stop
short of is the only one that was ever the problem. The trick that closes it
without a server -- planting a fixed ``sessionid`` in the browser once, by hand,
and re-creating a row with that key after each restore -- works, and it trades a
route for a manual browser step and a session key that never rotates.

So the short thing is a URL, because a URL is the one instruction a shell can
give a browser::

    $ xdg-open http://localhost:8000/dev-login/akaihola/

The fix
=======

``ylaneenkasvit/dev_login.py`` is the view: look the username up, refuse an
inactive account, name ``AUTHENTICATION_BACKENDS[0]`` as the backend that
``login`` wants, log in, redirect to ``/admin/``. Seventeen statements.

Everything else in the change is about where it exists.

* ``common_settings`` reads ``DEV_LOGIN`` from ``KASVIMUSEO_DEV_LOGIN`` and
  defaults it off.
* ``dev/kasvimuseo`` exports the variable to every container it starts, so the
  development server has the route without anything being turned on by hand,
  and ``KASVIMUSEO_DEV_LOGIN=`` turns it off for a session.
* ``ylaneenkasvit/urls.py`` registers the route only when the setting is on --
  the gate is the absence of the URL rather than a check inside a view that is
  always routed.
* ``ylaneenkasvit/dev_login.py`` checks the setting as well, for a caller that
  reaches it some other way.
* ``test_settings`` turns it off explicitly, because ``dev/kasvimuseo`` exports
  the variable to the test container too and a suite whose URLconf depends on
  the environment asserts nothing.

``kasvimuseo/tests/test_dev_login.py`` covers both states: the route logs an
account with an unusable password in and the next request reaches the admin;
an unknown or inactive username is a 404; with the setting off the path does
not resolve and the view raises ``Http404`` when called directly; and
``common_settings`` is read back with the variable set and unset, so the
default cannot drift.

Measured rather than argued, on the production dump restored locally: the
route answers 302 to ``/admin/`` and sets a ``sessionid``, ``curl`` following
it gets the dashboard with ``akaihola`` on it and no login form, Chromium
driven to the URL lands on ``/admin/`` with the same result, and the same
server started with ``KASVIMUSEO_DEV_LOGIN=`` answers 404.

What this is not
================

It is not a way into production. The route needs an environment variable that
Ansible does not write into ``uwsgi.ini``, and if it somehow were set there,
the view would still only log in accounts that already exist -- but the point
is the first half: the URL is not in that server's URLconf at all.

It is not ``DEBUG``-gated, and that is the deliberate part. Issue 051 is
production running with ``DEBUG`` on, from an untracked settings file nobody
was reading, for an unknown length of time. Any gate that trusts ``DEBUG``
would have been open there, which is the whole argument for a variable that
only the development harness sets.
