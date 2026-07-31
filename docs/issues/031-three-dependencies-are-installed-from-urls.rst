====================================================================
Issue 031: Three dependencies are installed from URLs, not from PyPI
====================================================================

:Status: Open
:Severity: Medium
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: 032 -- **met**: deleting ``fabfile.py`` removed ``flax``, one of
    the three
:Blocks: 036 -- Stage 0
:Related: 032
:Decision: undecided
:Resolution: (none yet)

Problem
=======

Three requirements were fetched over the network from places that are not a
package index. Two of the three have since gone, each with the thing that
wanted it, and the annotations below say which; **``django-jqm`` is what is
left**, and it is the one that mattered, being the only one of the three in
production.

``django-jqm`` (``production.txt``)
    ``https://github.com/akaihola/django-jqm/archive/1.1.0.2.zip`` -- a
    personal fork. Every production build depends on that GitHub URL being
    reachable and unchanged. The package is small: seven templates, two static
    files and three near-empty modules.

``flax`` (``dev.txt``) -- **gone**
    ``git+https://github.com/akaihola/django-flax@868c863...`` -- pinned to a
    commit, so at least reproducible, but still a personal repository. It was
    used only by ``fabfile.py``, and issue 032 deleted that file and both of
    the lines in ``dev.txt`` that existed for it, ``flax`` and
    ``Fabric==1.6.0``, having established that ``ansible/install.yaml`` and
    ``dev/kasvimuseo`` cover everything it did.

``podman-compose`` (``integration-tests.txt``) -- **gone**
    ``https://github.com/containers/podman-compose/archive/devel.zip`` --
    pinned to a **moving branch**, not a release or a commit, so what it
    installed changed without notice. It was there for the browser suite's
    ``docker-compose.yml``, and issue 017 deleted both the suite and
    ``requirements/integration-tests.txt`` with it, so this third one is no
    longer a live problem. Two are: the title and the count above are left as
    they were filed, and this is the correction rather than a rewrite.

None have a version history that can be reasoned about, which is why
``docs/dependency-inventory.rst`` has to list them separately from the other
49 packages.

Impact
======

Builds are not reproducible and not offline-capable. A GitHub outage, a renamed
repository or a deleted account breaks production deployment, not just
development. ``devel.zip`` in particular meant the integration test environment
could change under the project with no commit to show for it -- which is no
longer true, because that environment is gone (issue 017).

``django-jqm`` is the one that matters, because it is a production dependency,
and with ``flax`` gone as well it is the only one left. ``README.rst`` names
this issue as the reason the image build "goes red without anybody changing
anything" -- and that entry, which counted two, is now corrected to one, since
``flax`` was in ``dev.txt`` and ``dev/Containerfile`` installs
``production.txt`` alone. So the image never had more than the one URL that
could fail it.

Options
=======

``django-jqm``
    **Vendor it into the repository.** It is small, it is a fork nobody else
    maintains, and vendoring turns the Django-version fixes its templates will
    need during the upgrade into ordinary in-repo edits rather than a
    round-trip through another repository. Upgrade plan Stage 0.

``flax``
    Nothing left to do: it went with ``fabfile.py``, since
    ``ansible/install.yaml`` already did the same job. See issue 032, which
    also records what that file was the only copy of.

``podman-compose``
    Nothing left to do: it was development tooling for the browser suite, and
    both went with issue 017.
