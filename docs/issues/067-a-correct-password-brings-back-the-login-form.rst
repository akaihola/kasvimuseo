==============================================================================
Issue 067: A correct password brings back the login form
==============================================================================

:Status: Fixed
:Severity: High
:Area: dev environment / settings
:Reported: 2026-08-03
:Source: Maintainer report. ``dev/kasvimuseo app build``, ``db restore``,
    ``db upgrade-photologue`` and ``KASVIMUSEO_PORT=8000 dev/kasvimuseo app
    run`` on ``master`` at b7ea04b, then the admin: a wrong password gives the
    error it should, a right one gives the login form back, and every
    ``/admin/`` address is the login form
:Evidence: ``kasvimuseo/tests/test_settings_cookie_security.py`` --
    ``test_the_development_server_serves_plain_http`` predates this issue and
    passed throughout it, which is the point: it read the template rather than
    anything the server loads. It now imports the settings module the server
    runs on, beside ``test_the_development_relaxation_is_in_a_tracked_file``
    and ``test_the_superseded_template_is_gone``, which assert the thing the
    values alone cannot
:Depends on: (none)
:Blocks: (none) -- but nothing in the admin can be worked on from a browser
    that meets this, 044 included
:Related: 059 -- the change that introduced the value. It added the relaxation
    to the development template, which is the one place a development checkout
    does not read
    048 -- the same mechanism, found the same way: a setting added to
    ``local_settings.development.py`` after a developer's copy was made, and
    discovered from a browser
    044 -- the browser this is about, on another machine over the tailnet;
    the loopback browser that would have hidden this is the one this project
    does not use
    050 -- the rule this fix keeps: nothing that has to be right is left in an
    untracked file
    025, 026 -- the settings this project already reads from the environment
    rather than from an untracked file, for the same reason
:Decision: Ruled on 2026-08-03: **option 4**, a tracked development settings
    module. Four were put to the maintainer -- (1) name every setting a copy of
    the template is missing, as a note; (2) the same detection, but refuse to
    start; (3) read the relaxation from an environment variable
    ``dev/kasvimuseo`` sets, so it travels with a tracked file; (4) move the
    development settings into a tracked module and leave ``local_settings.py``
    for what is particular to one machine. The first two leave the settings
    where they are and report on them; the third fixes these two settings and
    not the class; the fourth removes the class, and was chosen for that
:Resolution: Fixed in 6469403, as ruled. ``ylaneenkasvit/development_settings.py``
    is tracked and holds everything ``local_settings.development.py`` held;
    ``dev/kasvimuseo`` runs the application on it, the template is deleted, and
    ``local_settings.py`` is optional and applied last. See "How it was fixed"
    below.

Problem
=======

As reported, and as ``master`` was at b7ea04b for anyone whose checkout
predates issue 059.

The development server issues its session and CSRF cookies with the ``Secure``
attribute, over plain HTTP::

    $ curl -sSi http://localhost:8000/admin/ | grep -i set-cookie
    Set-Cookie: csrftoken=2yMQi11wmgDPld70CbizDSzd8KHJWGt9; expires=Mon, 02-Aug-2027 18:59:09 GMT; Max-Age=31449600; Path=/; secure

A browser refuses to store a ``Secure`` cookie that arrived over ``http://``
unless the origin is one it already trusts, and it trusts loopback. So the
session cookie a successful login issues is dropped by the browser, the next
request arrives with no session, and Django's admin does what it does for an
anonymous request: it shows the login form. Nothing is logged, nothing is
displayed, and the password was in fact correct.

How it reproduces
=================

Measured against the reported server, in Chromium, with a throwaway superuser:

* ``http://localhost:8000/admin/`` -- **logs in**. Chromium treats a loopback
  origin as trustworthy and keeps the ``Secure`` cookies anyway. This is the
  case that hides the defect, and it is why the report and the reproduction
  have to name the origin rather than the port.
* ``http://192.168.1.88:8000/admin/`` with an empty cookie jar -- no cookie is
  stored at all, and the login ``POST`` is answered ``403``: with no
  ``csrftoken`` cookie there is nothing for ``CsrfViewMiddleware`` to compare
  the form's token against.
* ``http://192.168.1.88:8000/admin/`` carrying a ``csrftoken`` cookie without
  ``Secure`` -- **the report, exactly**. That cookie is what a browser that
  used this server before 059 still holds: it has a year's expiry, it is sent
  over plain HTTP, and Django 1.6 renders the form token from the cookie it
  receives. So CSRF passes, a wrong password is answered with the form error
  and a right one authenticates -- and then the session cookie is dropped for
  being ``Secure``, and the form comes back. Both halves of the report, from
  one cause.

Why it was like this
====================

``ylaneenkasvit/local_settings.development.py`` was a *template*, not a
settings file. ``dev/kasvimuseo`` copied it to the untracked
``ylaneenkasvit/local_settings.py`` when a checkout had none::

    ensure_local_settings() {
        local settings=$REPO/ylaneenkasvit/local_settings.py
        if [ ! -f "$settings" ]; then
            cp "$REPO/ylaneenkasvit/local_settings.development.py" "$settings"
            ...

and never afterwards -- deliberately, so that a developer's edits survive. Issue
059 marked both cookies ``Secure`` in ``common_settings`` for production and
relaxed them in the template for development. The relaxation was correct, and
it reached nobody who had cloned before it was written. A checkout made earlier
kept the production value, and the maintainer's did.

The script already knew this could happen. Issue 048 had added a note for the
one setting that had gone stale before::

    if ! grep -q MEDIA_FALLBACK_URL "$settings"; then
        echo "Note: your ylaneenkasvit/local_settings.py predates MEDIA_FALLBACK_URL," >&2

-- one literal, for the setting that was last to be noticed, added after that
one was found from a browser too. What 048 and 067 have in common is not the
setting; it is that a template cannot deliver anything to a checkout that
already exists.

The tests did not catch it because the assertion that existed --
``test_the_development_server_serves_plain_http`` -- loaded the template by
path and ran its ``modify()`` over a dictionary. It asserted what a *new*
checkout would get. No test could see what the running server had, because what
the running server had was in a file no test may depend on.

How it was fixed
================

``ylaneenkasvit/development_settings.py``, tracked, built on
``common_settings`` the way ``test_settings`` is, holding everything the
template held: ``DEBUG`` (via ``KASVIMUSEO_DEBUG``, which the image sets),
``django_extensions``, the two cookie settings, the database connection from
the environment, ``STATIC_*``, ``MEDIA_*`` including 048's fallback, and
``ALLOWED_HOSTS``. ``dev/kasvimuseo`` passes
``DJANGO_SETTINGS_MODULE=ylaneenkasvit.development_settings`` to every container
it runs -- in the ``podman run`` arguments rather than in the image, so that a
change to it needs no ``app build`` -- and ``dev/Containerfile``'s own ``ENV``
names the same module for anyone who runs the image by hand. The suite and the
browser tests name ``test_settings`` after it and win, as they did before.

``local_settings.development.py`` is deleted, and with it ``ensure_local_settings``.
Nothing is copied into place any more, so nothing can be stale. What is left in
its place is a note for the copies that already exist: they are applied over the
tracked settings, so ``dev/kasvimuseo`` recognises one and says it can be cut
down or deleted.

``ylaneenkasvit/local_settings.py`` still exists and is still read, last, by the
same ``modify(globals())`` protocol production uses -- a machine that needs
something particular can still have it. It is no longer where anything that has
to be right is kept.

Three tests, in ``kasvimuseo/tests/test_settings_cookie_security.py``: the
existing one now imports the module the server actually loads, one asserts that
the file is not one the repository excludes, and one asserts the template is
gone. Together they fail if the relaxation goes back to being unreachable,
which is the defect -- the values on their own were right the whole time.

What is not fixed here
======================

A ``local_settings.py`` written before this change still shadows the tracked
values with the ones it was copied with, and for a copy that was never edited
those are the same values. The note says so; nothing deletes a developer's file
for them. It names the ``.pyc`` too, because Python 2.7 imports one that has no
source beside it -- deleting only the ``.py`` would leave the settings in force
and the note gone, which is the same trap ``ansible/secure-production.yaml``
avoids in production by deleting both (issue 050).

See also
========

:doc:`059 <059-cookies-are-not-secure-and-no-page-refuses-to-be-framed>` -- the
change this issue is the cost of, and where the production reasoning is written
out. Its ruling stands: what moved is where development says otherwise.

:doc:`048 <048-the-dev-server-loads-photos-from-the-production-media-host>` --
the same mechanism, one setting earlier, and the note whose narrowness this
replaces.

:doc:`044 <044-large-admin-pages-are-truncated-for-a-remote-browser>` -- the
browser on another machine, which is the one this defect needs and the one this
project has.
