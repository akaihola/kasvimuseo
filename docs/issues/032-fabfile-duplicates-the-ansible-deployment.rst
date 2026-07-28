==================================================================
Issue 032: fabfile.py duplicates the Ansible deployment, in Python 2
==================================================================

:Status: Open
:Severity: Low
:Area: deployment / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``fabfile.py`` describes a complete deployment -- ``bootstrap``,
``configure_nginx``, ``configure_postgresql``, ``configure_supervisor``,
``create_db``, ``install_django``, ``collectstatic``, ``syncdb``, ``update`` --
by importing them from ``flax``, a personal Fabric helper library.

``ansible/install.yaml`` does the same work, and it is the one that is
maintained: it configures nginx, PostgreSQL with PostGIS, certbot and uWSGI,
and ``README.rst`` points at it for the database backup path. ``fabfile.py``
still references ``supervisor``, which the Ansible setup does not use, and
``bitbucket.com/akaihola/ylaneenkasvit.git`` as the repository.

The Fabric route also cannot survive the Python 3 migration as written.
Fabric 1.x is Python 2 only through 1.14.1; 1.15.0 added Python 3 support, and
Fabric 2.x/3.x are a rewrite with an incompatible API. Porting means rewriting
the deployment, not bumping a pin.

Impact
======

Two deployment mechanisms, one of them stale, is a trap for whoever deploys
next -- particularly since the stale one looks authoritative sitting in the
repository root. It also keeps ``Fabric``, ``flax`` and a GitHub dependency in
``dev.txt`` for no return.

Options
=======

Delete ``fabfile.py`` and remove ``Fabric`` and ``flax`` from ``dev.txt``.
Confirm first that ``ansible/install.yaml`` genuinely covers everything still
wanted from it -- ``clone_db`` and ``manage`` are the two worth checking, and
``dev/kasvimuseo`` now covers both locally.

If any of it is still wanted, the alternative is a rewrite against Fabric 3,
which is a real piece of work and should be a deliberate decision rather than a
side effect of the upgrade.

See also
========

Issue 031 -- ``flax`` is one of the three URL dependencies.
``docs/upgrade-plan.rst`` Part 5.
