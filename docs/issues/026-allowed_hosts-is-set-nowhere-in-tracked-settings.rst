===========================================================
Issue 026: ALLOWED_HOSTS is set nowhere in tracked settings
===========================================================

:Status: Fixed
:Severity: Medium
:Area: settings / deployment
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``kasvimuseo/tests/test_settings_allowed_hosts.py`` -- added with the fix. It pins that ``hosts_from_env`` has no default and names the missing variable, and that an unnamed ``Host`` header is refused once ``DEBUG`` is off. Nothing pinned the old behaviour: an absent setting is not something a test can catch, and the suite never sees the real list anyway, because Django 1.5's ``setup_test_environment`` replaces ``ALLOWED_HOSTS`` with ``['*']`` for the duration of a run.
:Depends on: (none)
:Blocks: 051 -- turning production's ``DEBUG`` off requires a deployment that sets ``ALLOWED_HOSTS``, which is what this issue built
:Related: 025 -- the same file, and the same question of what the server carries that the repository does not
    049 -- the deploy that carries this change to the server, and the same split between a repository half and a server half
:Decision: Both cases were true at once, and the maintainer's look at the server settled it. Set ``ALLOWED_HOSTS`` from the environment with no default (``KASVIMUSEO_ALLOWED_HOSTS``, read by ``hosts_from_env``, exactly 025's idiom) and have Ansible supply it from a **tracked** variable, ``kasvimuseo_allowed_hosts`` in ``ansible/vars/main.yml`` -- not the vault, because a host name is not a secret and putting it in the tracked files is the point. Turning production's ``DEBUG`` off is 051, and it can only happen after this change is deployed.
:Resolution: Commit `PENDING` -- ``ALLOWED_HOSTS`` is set in the tracked settings and written into the production process environment by ``uwsgi.ini``. That is the whole of the repository half. It does not turn ``DEBUG`` off on the server, which is where the information disclosure actually is: see 051.

.. warning::

   **Production is serving with DEBUG on.** The maintainer read the
   server on 2026-07-31: ``/home/kasvimuseo/.local/lib/python2.7/site-packages/ylaneenkasvit/local_settings.py``
   exists, is untracked, and its whole content is ``settings['DEBUG'] = True``
   and ``settings['TEMPLATE_DEBUG'] = True``. So settings, SQL and full
   tracebacks are on every error page today. This issue is what makes turning
   it off possible; :doc:`051 <051-production-serves-with-debug-on-behind-an-untracked-local-settings>`
   is turning it off.

Problem
=======

``ALLOWED_HOSTS`` does not appear anywhere in the repository -- not in
``common_settings.py``, not in ``ylaneenkasvit_settings.py``, not in
``kajala_settings.py``, not in ``local_settings.development.py``, and not in
the Ansible playbooks.

Django 1.5 is unambiguous about what that means. From
``django/http/request.py`` in 1.5.12::

    allowed_hosts = ['*'] if settings.DEBUG else settings.ALLOWED_HOSTS
    if validate_host(host, allowed_hosts):
        return host
    else:
        raise SuspiciousOperation(
            "Invalid HTTP_HOST header (you may need to set ALLOWED_HOSTS): %s" % host)

With ``DEBUG = False`` and an empty ``ALLOWED_HOSTS``, **every request raises
``SuspiciousOperation``**. The site would not serve a single page.

Production evidently does serve pages, so one of two things is true, and it
matters a great deal which:

1. There is a hand-placed ``local_settings.py`` on the server, picked up by the
   ``try: from local_settings import *`` hook at the bottom of
   ``ylaneenkasvit_settings.py``. It is not tracked and not created by
   ``ansible/install.yaml``, so it exists only as an artefact on that host.
2. ``KASVIMUSEO_DEBUG`` is set in the production environment, so
   ``DEBUG = True`` and the check is bypassed by ``['*']``. This would mean
   **production is running with DEBUG on**, which leaks settings, SQL and full
   tracebacks on every error page.

This analysis could not determine which, and the difference is not visible from
the repository. Both turned out to be true -- see "What the server actually
carries" below.

Impact
======

If (1): the deployment is not reproducible. Re-running the Ansible playbook
onto a fresh host produces a site that 400s on every request, and the cause is
a file nobody has a copy of.

If (2): a live information-disclosure problem, independent of everything else
in this document.

Options
=======

First **find out which it is** -- check for ``local_settings.py`` on the server
and for ``KASVIMUSEO_DEBUG`` in the uWSGI environment. Then:

* Set ``ALLOWED_HOSTS`` explicitly in ``ylaneenkasvit_settings.py`` or from the
  environment, and have Ansible provide it.
* If ``DEBUG`` is on in production, turn it off, which will require doing the
  above first or the site will stop responding.

What the server actually carries
================================

The repository was read first, and it is unanimous as far as it goes. Nothing
under ``ansible/`` sets ``KASVIMUSEO_DEBUG``: the production process
environment is written by ``ansible/roles/akaihola.uwsgi/templates/uwsgi.ini``,
whose only ``env =`` lines were ``KASVIMUSEO_SECRET_KEY`` and
``KASVIMUSEO_DB_PASSWORD`` (issue 025's work); the systemd unit beside it,
``templates/uwsgi_systemd``, has no ``Environment=`` line; the one
``environment:`` block in ``ansible/install.yaml`` (lines 117-120) sets the same
two variables for ``collectstatic``; and ``ansible/vars/main.yml``,
``ansible/host_vars/`` and ``ansible/templates/nginx-site.conf.j2`` set neither
``DEBUG`` nor ``ALLOWED_HOSTS``. ``KASVIMUSEO_DEBUG=1`` appears exactly once in
the repository, at ``dev/Containerfile:70``, which is the development image.

So under Ansible alone production would run ``DEBUG = False`` with an empty
``ALLOWED_HOSTS`` and refuse every request. It serves pages, so something
outside Ansible was making the difference, and that was as far as the
repository could take it -- nothing here can reach the server.

The maintainer looked, on 2026-07-31, and the answer is **both cases at once**::

    root@vps763955:/home/kasvimuseo# cat /home/kasvimuseo/uwsgi.ini
    [uwsgi]
    module = ylaneenkasvit.wsgi
    socket = /home/kasvimuseo/wsgi.sock
    ...

    root@vps763955:/home/kasvimuseo# find -name local_settings.py
    ./.local/lib/python2.7/site-packages/ylaneenkasvit/local_settings.py

    root@vps763955:/home/kasvimuseo# cat .local/lib/python2.7/site-packages/ylaneenkasvit/local_settings.py
    import os


    def modify(settings):
        settings['DEBUG'] = True
        settings['TEMPLATE_DEBUG'] = True

Case (1) is how it happens: an untracked, hand-placed ``local_settings.py``,
picked up by the ``try: from local_settings import *`` hook at the bottom of
``ylaneenkasvit_settings.py``. Case (2) is what it does: that file's entire
content is ``DEBUG = True``, so ``get_host`` takes the ``['*']`` branch and the
missing ``ALLOWED_HOSTS`` has never been reached. Production is therefore
serving with settings, SQL and full tracebacks on every error page, which is
the live problem this issue's option (2) described, arrived at through option
(1)'s mechanism.

Two things fall out of the same output, neither of them this issue:

* The server's ``uwsgi.ini`` has no ``env =`` lines at all, so it predates
  025's change and no deploy has run since. That is :doc:`049
  <049-production-still-runs-the-old-secret-key-and-database-password>`,
  confirmed from the file rather than inferred.
* The site's ability to answer a request at all currently depends on an
  untracked file in a ``site-packages`` directory that ``pip install --upgrade``
  writes to. A ``-t code`` run that removed it would take the site down with a
  400 on every request, and nothing would say why.

What was done
=============

The repository half, following 025's idiom exactly:

``ylaneenkasvit/common_settings.py``
    ``hosts_from_env(name)`` beside ``secret_from_env``, sharing its
    ``_from_env`` core, so there is one place that decides what a missing value
    means. No default, for the reason 025 had none: an empty list makes every
    request a ``SuspiciousOperation`` and ``['*']`` switches the check off, so
    both possible fallbacks answer a misconfiguration silently. The value is a
    comma-separated list, because a process environment holds strings.

``ylaneenkasvit/ylaneenkasvit_settings.py``, ``ylaneenkasvit/kajala_settings.py``
    ``ALLOWED_HOSTS = hosts_from_env('KASVIMUSEO_ALLOWED_HOSTS')``.

``ylaneenkasvit/test_settings.py``
    Names its hosts literally, as it does its ``SECRET_KEY``, so the suite needs
    no variable set. The suite never reads them -- Django 1.5's
    ``setup_test_environment`` replaces ``ALLOWED_HOSTS`` with ``['*']`` for a
    test run -- but the browser tests serve these settings from gunicorn,
    outside that.

``dev/kasvimuseo``
    Passes ``KASVIMUSEO_ALLOWED_HOSTS`` into the app container beside the
    secret key, defaulting to ``*``: a development server is reached under
    whatever name its developer published it, and nothing on it is production.

``ansible/vars/main.yml``, ``ansible/roles/akaihola.uwsgi/templates/uwsgi.ini``, ``ansible/install.yaml``
    ``kasvimuseo_allowed_hosts`` is a tracked variable, not a vaulted one --
    ``kasvit.ambitone.com`` plus the two names the maintainer reports also reach
    the site, ``www.kasvit.ambitone.com`` and ``vps763955.ovh.net``. The uWSGI
    template joins it with commas into an ``env =`` line, and ``collectstatic``
    gets it too, since importing the settings now needs it. Tracked rather than
    vaulted because a host name is not a secret and because being in the
    repository is the whole point: the value that used to live only on the
    server now travels with the code.

Measured, in the container: the suite passes (413 tests, seven of them the new
ones), the browser tests pass (11), and ``ylaneenkasvit_settings`` imported with
the untracked ``local_settings.py`` hidden gives
``ALLOWED_HOSTS = ['kasvit.ambitone.com', 'www.kasvit.ambitone.com',
'vps763955.ovh.net']`` with ``DEBUG = False``, while the same import with the
variable unset raises ``ImproperlyConfigured: KASVIMUSEO_ALLOWED_HOSTS is not
set...`` rather than starting.

What is left, which is not this issue
=====================================

Deleting that ``local_settings.py`` and letting ``DEBUG`` be false is
:doc:`051 <051-production-serves-with-debug-on-behind-an-untracked-local-settings>`.
It is filed separately on 049 and 050's precedent -- the repository half is done
here, the act that ends the disclosure is on a machine this repository cannot
reach -- and the order is not optional: the deploy that sets ``ALLOWED_HOSTS``
has to land first, or removing the file turns every request into a 400.

See also
========

Issue 025 -- the same file, and the same underlying question of what the
deployment actually carries that the repository does not.
