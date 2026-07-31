==================================================================
Issue 021: gunicorn is an INSTALLED_APP for a command that is gone
==================================================================

:Status: Fixed
:Severity: Low
:Area: settings / dependencies
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: (none)
:Blocks: 036 -- Stage 0
:Related: 029 -- the real gunicorn constraint, as distinct from this cosmetic one
:Decision: Remove ``'gunicorn'`` from ``INSTALLED_APPS`` and keep the pin in ``requirements/production.txt``. It is the production server, and since issue 044 the development server too, so the dependency has more use now than when this was filed -- it is only the *app* entry that is dead.
:Resolution: 0c82b49 -- with issues 020 and 033, which edit the same six lines

Problem
=======

``ylaneenkasvit/common_settings.py`` lists ``gunicorn`` in ``INSTALLED_APPS``.

A WSGI server is not a Django application. It was listed there for one reason:
gunicorn used to ship a ``run_gunicorn`` management command, which only worked
if the package was an installed app.

That command no longer exists. Checking the shipped contents of each release:

=================== ===========================================
gunicorn            ``management/commands/run_gunicorn.py``
=================== ===========================================
0.17.4 (pinned)     present
18.0 – 19.6.0       present
**19.7.1** +        **removed**
=================== ===========================================

The project does not use the command in any case -- ``ylaneenkasvit/wsgi.py``
is the entry point, and the Dockerfile runs ``manage runserver``.

Impact
======

Harmless today, but it is dead configuration that will confuse whoever does the
upgrade, and gunicorn ≥ 19.7.1 has no ``management`` package at all.

Options
=======

Remove ``'gunicorn'`` from ``INSTALLED_APPS``. Keep the dependency itself --
it is still the production server.

Decision
========

Done as described. One line out of ``INSTALLED_APPS``; ``gunicorn==0.17.4``
stays in ``requirements/production.txt``, and the rebuilt development image
still has it -- ``import gunicorn`` answers ``0.17.4`` in the image that no
longer has ``indexer`` or ``paging`` (issue 020).

Keeping it is not a formality. When this was filed, gunicorn ran only in
production; since issue 044 it is also what ``dev/kasvimuseo app run`` starts,
because ``manage.py runserver`` is wsgiref and answers HTTP/1.0 without a
``Content-Length``, which is what let a truncated admin page look complete for
as long as it did. So the package is load-bearing in both environments, and it
is only the ``INSTALLED_APPS`` entry -- the half that exists for a management
command deleted in 19.7.1 and never used here -- that this issue removes.

Nothing about how gunicorn is *run* changes, and nothing needed to: it is
invoked as ``gunicorn ylaneenkasvit.wsgi:application`` in ``dev/kasvimuseo``
and through ``ylaneenkasvit/wsgi.py`` in production. Neither path asks Django
what its installed apps are.

Issue 029 -- the ``setuptools`` ceiling, the real gunicorn constraint -- is
untouched. Its own fix landed on ``master`` while this branch was open and
writes that constraint into ``requirements/production.txt`` as a comment
directly above the pin, so the line this issue keeps now has seven lines of
explanation attached to it saying why it is kept and what happens to it at
Stage 10. Nothing here changes that comment or the pin under it.

Verification
============

Shared with issues 020 and 033, and written out in full in issue 020: the
rebuilt image, the empty greps, ``dev/kasvimuseo app test`` (406 passed),
``manage.py validate`` (0 errors), and the public pages, the two reports and
the admin change lists all answering ``200`` over HTTP from ``dev/kasvimuseo
app run`` -- which is to say, served by the gunicorn this issue took out of
``INSTALLED_APPS``, after it was taken out.

See also
========

Issue 029 covers a real gunicorn constraint, as distinct from this cosmetic one.
