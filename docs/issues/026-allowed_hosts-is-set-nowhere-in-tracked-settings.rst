===========================================================
Issue 026: ALLOWED_HOSTS is set nowhere in tracked settings
===========================================================

:Status: Open
:Severity: Medium
:Area: settings / deployment
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none -- ``grep -rn ALLOWED_HOSTS`` over the whole repository returns nothing)
:Depends on: (none)
:Blocks: (none)
:Related: 025 -- the same file, and the same question of what the server carries that the repository does not
:Decision: undecided
:Resolution: (none yet)

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
the repository.

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

See also
========

Issue 025 -- the same file, and the same underlying question of what the
deployment actually carries that the repository does not.
