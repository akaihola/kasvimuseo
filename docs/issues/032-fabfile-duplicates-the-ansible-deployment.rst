====================================================================
Issue 032: fabfile.py duplicates the Ansible deployment, in Python 2
====================================================================

:Status: Fixed
:Severity: Low
:Area: deployment / cleanup
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: (none)
:Blocks: 031 -- removes the ``flax`` third of it
    036 -- Stage 0
:Related: 031
:Decision: Delete it, and write down the one thing it was the only copy of.
    Every task the file offered is covered twice over -- by
    ``ansible/install.yaml`` on the server and by ``dev/kasvimuseo`` here --
    and the two comments added to it since have their live copies elsewhere;
    the measurements are in "What was checked" below. What deleting it did
    cost is the second site's deployment: ``kajala()`` was the only tracked
    description of how *Kajalan kasvimaat* was ever installed, so it is
    transcribed into "What the second site's entry recorded", below, in the
    same change that removed the file. Whether that site still exists is a
    separate question, and it is in :doc:`incoming` rather than answered here.
:Resolution: 51ae5fc -- deletes ``fabfile.py`` and the two ``requirements/dev.txt``
    lines that existed for it.

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

What was checked
================

The two the issue asked about
-----------------------------

``clone_db``
    Covered, and by two independent paths. ``dev/kasvimuseo``'s ``db_fetch``
    dumps production over SSH into ``.dev/backups/production.sql`` and
    ``db restore`` loads it, adapting the dump to a current PostgreSQL as it
    goes; both are the first thing ``README.rst`` documents. For anyone without
    an SSH account there is the Ansible route instead -- ``ansible-playbook -t
    backup -e backup_database=/backup-dir ansible/install.yaml``, the ``Back up
    the database`` and ``Fetch database backup from host`` tasks in
    ``install.yaml`` -- and ``db fetch`` names that route itself in the error it
    dies with when the password is missing.

``manage``
    Covered. ``dev/kasvimuseo app manage <args>`` runs any management command in
    the Python 2.7 container, starting and stopping the cluster around it. On
    the server the only management command the deployment actually runs is
    ``collectstatic``, and ``install.yaml`` runs it through ``django_manage``
    with the settings module named and the three environment values the
    settings now insist on.

The rest of the file
--------------------

Every remaining task has an Ansible equivalent: ``configure_nginx`` →
``nginxinc.nginx``, ``configure_postgresql`` + ``create_db`` +
``create_db_user`` → ``geerlingguy.postgresql`` with ``postgresql_databases``
and ``postgresql_users`` in ``ansible/vars/main.yml``, ``install_django`` +
``install_project`` + ``update_code`` → the ``pip`` task that installs the
package from git, ``restart_django`` → the ``akaihola.uwsgi`` role.
``configure_supervisor`` is the one with no equivalent, and deliberately so:
the Ansible deployment runs uWSGI, not supervisor. Two further signs the file
had stopped describing this system: it names
``bitbucket.com/akaihola/ylaneenkasvit.git`` as the repository, where
``install.yaml`` installs ``git+ssh://git@bitbucket.org/akaihola/kasvimuseo.git``,
and it configures ``gunicorn`` as the production web server, which since the
Ansible setup has been uWSGI behind nginx.

The two comments added since
----------------------------

Both were checked against the places the facts live now, and neither was the
only copy:

``env.pip_args = '--no-deps'`` (issue 027)
    The live copy is ``dev/Containerfile``'s comment on the same flag, quoted
    verbatim in 027's own file. 027 had already written the sentence this
    deletion needs -- that the fabfile comment describes what ``--no-deps`` now
    is "until issue 032 deletes the file" -- so the only thing left to do here
    was to put that clause in the past tense, which this change does.

``env.db_password = os.environ['KASVIMUSEO_DB_PASSWORD']`` (issue 025)
    The same fact, with the same explanation, is in
    ``ylaneenkasvit/kajala_settings.py``, which is where the Kajala database
    password is actually read; ``ansible/vars/main.yml`` does the equivalent for
    Yläne out of the vault. 025's own file describes the fabfile line, and that
    paragraph is now past tense.

The rest of the tree
--------------------

Nothing outside the documentation referred to the file. In particular
``README.rst`` never described the Fabric route at all -- it documents
``dev/kasvimuseo`` and Ansible and nothing else -- so it needed no change, and
neither did ``setup.py``, ``dev/`` or ``.github/``. What was left was prose:
``docs/dependency-inventory.rst``, ``docs/upgrade-plan.rst`` Part 5 and its
Stage 10 table, issues 025, 027 and 031, and this register. All are past tense
now. ``fabric``'s version table stays in the inventory, since that document
records what was surveyed rather than what is installed, with a line saying the
package is gone.

What the second site's entry recorded
=====================================

``fabfile.py``'s ``kajala()`` task was the only tracked description of how
*Kajalan kasvimaat* -- the second site ``docs/index.rst`` says this codebase
serves, whose settings module ``ylaneenkasvit/kajala_settings.py`` is still
here and still maintained -- was deployed. ``ansible/hosts`` names one host,
and ``ansible/vars/main.yml`` names only ``ylaneenkasvit`` databases, nginx
servers and certbot domains, so Ansible has never known about it. Deleting the
file without transcribing this would have deleted the record, so here it is as
it stood:

=========================== ==============================================
Host                        ``kala.ambitone.com`` -- a different machine
                            from Yläne's ``kasvit.ambitone.com``
Project root                ``/www/ylaneenkasvit`` (shared with Yläne)
Site root                   ``/www/kajalankasvit``
Project name                ``kajalankasvit``
Public host name            ``kajalankasvit.ambitone.com``
Django port                 ``11110``
Database name and user      ``kajalankasvit`` (password from
                            ``KASVIMUSEO_DB_PASSWORD``, issue 025)
Settings module             ``ylaneenkasvit.kajala_settings``
Static site                 ``static.kajalankasvit.ambitone.com`` →
                            ``/www/ylaneenkasvit/static/``
Media site                  ``media.kajalankasvit.ambitone.com`` →
                            ``/www/kajalankasvit/media/``
nginx                       ``client_max_body_size 10m;``
gunicorn timeout            240 s
=========================== ==============================================

Two things in it are worth reading rather than filing. The static site pointed
at the *Yläne* project root while the media site pointed at Kajala's own, which
is consistent with ``kajala_settings.py``: it overrides ``MEDIA_ROOT`` to
``SITE_ROOT/media`` and takes ``STATIC_ROOT`` from the common settings. And the
host is a different machine from the one Ansible deploys, so this was never a
second virtual host on the current server -- it was a second installation
somewhere else.

Whether that installation still exists is not a question this repository can
answer, and it is not this issue: it is filed in :doc:`incoming`, because the
answer decides between two quite different pieces of work -- teaching Ansible a
second host, or deleting ``kajala_settings.py`` and the sentence in
``docs/index.rst`` that promises two sites.

What this leaves of issue 031
=============================

031 filed three dependencies installed from URLs. ``podman-compose`` went with
issue 017, which deleted the browser suite's ``requirements/integration-tests.txt``
along with it; ``flax`` is gone with this change. **One is left**:
``django-jqm``, the ``production.txt`` entry installed from
``https://github.com/akaihola/django-jqm/archive/1.1.0.2.zip``, and it is the
one that mattered all along, being the only one of the three in production. Its
option is unchanged -- vendor it into the repository, at upgrade-plan Stage 0 --
and 031 stays open for it. 031's ``Depends on`` note is updated to say the
``flax`` third is done rather than that it will be.

See also
========

Issue 031 -- ``django-jqm`` is the one URL dependency left.
``docs/upgrade-plan.rst`` Part 5.
