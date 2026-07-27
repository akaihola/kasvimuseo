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
    $ dev/kasvimuseo db reset                 # delete the cluster entirely
    $ dev/kasvimuseo app manage <args>        # any manage.py command
    $ dev/kasvimuseo app test                 # unit tests; needs no database
    $ dev/kasvimuseo app shell                # shell in the Python 2.7 container

``app run`` and ``app manage`` start PostgreSQL if it is down and stop it again
when they exit, so the cluster only runs while it is needed. Started by hand
with ``db start``, it keeps running until ``db stop``.

Local settings live in ``ylaneenkasvit/local_settings.py`` (untracked, seeded
from ``local_settings.development.py``). Photos are loaded straight from
``media.kasvit.ambitone.com``. Mount them locally only if Django itself has to
read the image files::

    $ sshfs -o ro akaihola@kasvit.ambitone.com:/www/ylaneenkasvit/media media



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
