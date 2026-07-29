====================================================================
Issue 031: Three dependencies are installed from URLs, not from PyPI
====================================================================

:Status: Open
:Severity: Medium
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: 032 -- deleting ``fabfile.py`` removes ``flax``, one of the three
:Blocks: 036 -- Stage 0
:Related: 032
:Decision: undecided
:Resolution: (none yet)

Problem
=======

Three requirements are fetched over the network from places that are not a
package index:

``django-jqm`` (``production.txt``)
    ``https://github.com/akaihola/django-jqm/archive/1.1.0.2.zip`` -- a
    personal fork. Every production build depends on that GitHub URL being
    reachable and unchanged. The package is small: seven templates, two static
    files and three near-empty modules.

``flax`` (``dev.txt``)
    ``git+https://github.com/akaihola/django-flax@868c863...`` -- pinned to a
    commit, so at least reproducible, but still a personal repository. Used
    only by ``fabfile.py``.

``podman-compose`` (``integration-tests.txt``)
    ``https://github.com/containers/podman-compose/archive/devel.zip`` --
    pinned to a **moving branch**, not a release or a commit. What this
    installs changes without notice.

None have a version history that can be reasoned about, which is why
``docs/dependency-inventory.rst`` has to list them separately from the other
49 packages.

Impact
======

Builds are not reproducible and not offline-capable. A GitHub outage, a renamed
repository or a deleted account breaks production deployment, not just
development. ``devel.zip`` in particular means the integration test environment
can change under the project with no commit to show for it.

``django-jqm`` is the one that matters, because it is a production dependency.

Options
=======

``django-jqm``
    **Vendor it into the repository.** It is small, it is a fork nobody else
    maintains, and vendoring turns the Django-version fixes its templates will
    need during the upgrade into ordinary in-repo edits rather than a
    round-trip through another repository. Upgrade plan Stage 0.

``flax``
    Delete along with ``fabfile.py`` -- ``ansible/install.yaml`` already does
    the same job. See issue 032.

``podman-compose``
    Pin to a release or a commit at minimum. It is development tooling, so this
    is the least urgent of the three.
