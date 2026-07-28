Development setup
=================

The app is Django 1.5 on Python 2.7, which no longer exists in current
distributions, so it runs in a container. The database runs natively as a
throwaway PostgreSQL cluster inside the working copy. Everything is driven by
one script, ``dev/kasvimuseo``; all its state lives under ``.dev/`` and can be
deleted at any time.

Requirements: ``podman`` and a PostgreSQL client/server installation (any
version from 9.x up; 15 is known to work).

Build the app image once::

    $ dev/kasvimuseo app build

Copy the production database and load it locally::

    $ dev/kasvimuseo db fetch                        # -> .dev/backups/production.sql
    $ dev/kasvimuseo db restore .dev/backups/production.sql

``db fetch`` runs ``pg_dump`` over SSH. It needs an account on
``kasvit.ambitone.com`` whose key is authorised; override the default with
``KASVIMUSEO_PROD_SSH=user@host``. Without SSH access, produce the dump with
Ansible instead and restore that file::

    $ ansible-playbook -t backup -e backup_database=/backup-dir ansible/install.yaml
    $ dev/kasvimuseo db restore /backup-dir/vps763955.ovh.net/tmp/backup.sql

To work without any production data, build an empty database from the
migrations instead, and give yourself an admin account::

    $ dev/kasvimuseo db bootstrap
    $ dev/kasvimuseo app manage createsuperuser

Run the site at http://localhost:8000/ ::

    $ dev/kasvimuseo app run

Other commands::

    $ dev/kasvimuseo db start|stop|status     # PostgreSQL by hand
    $ dev/kasvimuseo db psql                  # psql on the local database
    $ dev/kasvimuseo media fetch              # photos the database references
    $ dev/kasvimuseo db reset                 # delete the cluster entirely
    $ dev/kasvimuseo app manage <args>        # any manage.py command
    $ dev/kasvimuseo app test                 # unit tests; needs no database
    $ dev/kasvimuseo app shell                # shell in the Python 2.7 container

``app run`` and ``app manage`` start PostgreSQL if it is down and stop it again
when they exit, so the cluster only runs while it is needed. Started by hand
with ``db start``, it keeps running until ``db stop``.

Production still runs PostgreSQL 10, so ``db restore`` adapts the dump to a
current server: it drops the PostGIS extension when PostGIS is not installed
locally (no table uses a spatial type) and the one index over ``abstime``, a
type removed in PostgreSQL 12. Both are reported as they are skipped.

Local settings live in ``ylaneenkasvit/local_settings.py``. It is untracked, so
``dev/kasvimuseo`` copies it from ``local_settings.development.py`` the first
time it runs the app; edit your copy freely. Without it the app falls back to
production's static URL and ignores the database environment variables.

Photos are loaded straight from ``media.kasvit.ambitone.com``, so the species
list, the planting labels and the admin need no local media. The printable and
compact species views do: Django opens the image files to read their
dimensions, and raises ``IOError`` if they are missing. Download exactly the
photos the database references -- no SSH needed, the media host is public::

    $ dev/kasvimuseo media fetch

That is 137 files and about 260 MB at the time of writing, and it skips what is
already there, so it is safe to re-run after restoring a newer dump. The whole
directory, including material no row points at, still needs SSH::

    $ rsync -a akaihola@kasvit.ambitone.com:/www/ylaneenkasvit/media/ media/



Documentation
=============

``docs/`` is a Sphinx project: this file, the issue register, the plans, and an
API reference generated from the source. Build it into ``.dev/docs/html/``::

    $ dev/kasvimuseo docs --open

It runs on the host's Python 3 through ``uv``, not in the app container, and
never imports the application -- see
``docs/issues/038-no-rendered-documentation.rst`` for why, and for how it should
change as the stack is upgraded. The toolchain is pinned in
``docs/requirements.txt``; nothing needs installing beforehand.

To rebuild automatically whenever a coding agent edits documentation or Python
source, register the hook in ``.claude/settings.json``. Agents cannot write that
file -- the harness masks it -- so this one is by hand::

    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Write|Edit|MultiEdit",
            "hooks": [
              {"type": "command", "command": "dev/docs-hook", "async": true}
            ]
          }
        ]
      }
    }

``async`` is the part that matters: the hook runs in the background and the
agent carries on. ``dev/docs-hook`` exits immediately for an edit that touches
nothing the documentation is built from, and a rebuild after one that does takes
about six seconds.

Reading the docs from another machine
-------------------------------------

::

    $ dev/kasvimuseo docs serve

Serves every checkout of the repository at once -- the main one and each
worktree, each from its own ``.dev/docs/html/`` -- on port 8800, bound to this
machine's Tailscale address, so it is reachable from the tailnet and from
nowhere else. ``/`` lists the checkouts; each is at ``/<branch>/``, the main
checkout also at the fixed ``/main/`` because its branch changes. Every page
gets a switcher in the corner that jumps to the same page in another checkout.

The list is re-read per request, so worktrees added or removed while it runs
need no restart. It serves what has been built and nothing else: a checkout
whose docs are missing says so, and building it is ``dev/kasvimuseo docs``
*in that checkout*. Stdlib Python 3 only -- ``--port`` and ``--bind`` override
the defaults.


Using Ansible for deployment, update and maintenance
====================================================

Before running ``ansible-playbook``, get the vault password from your password manager
and run::

    export ANSIBLE_VAULT_PASS=***********


Deployment
==========

    ansible-playbook ansible/bootstrap.yml
    ansible-playbook ansible/install.yml

Restoring the database on the server
------------------------------------

    ansible-playbook \
      -t restore \
      -e database_backup_to_restore=local/path/to/backup.sql \
      ansible/install.yaml

Updating the software
---------------------

    ansible-playbook -t code ansible/install.yaml


Maintenance
===========

Backing up the database
------------------------

    ansible-playbook \
      -t backup \
      -e backup_database=/backup-dir \
      ansible/install.yaml

Restoring the database in a development environment
---------------------------------------------------

    sudo -u postgres createdb -O ylaneenkasvit ylaneenkasvit
    sudo -u postgres psql -f /backup-dir/vps763955.ovh.net/tmp/backup.sql ylaneenkasvit

Updating code on the server
---------------------------

    ansible-playbook -t code ansible/install.yaml
