Issue 079: Django 2.0 removes the last 1.x APIs this project uses
=================================================================

:Status: Fixed
:Severity: Medium
:Area: platform / compatibility
:Reported: 2026-09-15
:Source: Backlog refill from upgrade plan Stage 11
:Evidence: 531 tests pass on Django 2.0.13 with no ``RemovedInDjango`` warning; both images build; ``check`` and the scoped migration check pass.
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the runtime upgrade programme
:Decision: Complete Stage 11 on Python 3.7 with the pins the upgrade plan names. Keep the later stages in issue 036.
:Resolution: d1b5f89 drops the removed APIs; c07bab2 updates two tests; 3d4e3f1 moves the pins.

Work
----

This issue is for the implementation agent. It tracks Stage 11 of :doc:`../upgrade-plan`.

Django 2.0 removes three things the code still uses:

#. ``allow_tags`` on three ``ModelAdmin`` methods in ``kasvimuseo/admin.py``.
#. ``use_for_related_fields`` on ``ObservationManager`` in ``kasvimuseo/models.py``.
#. ``include(admin.site.urls)`` in ``ylaneenkasvit/urls.py``, a 3-tuple include.

The stage also moves the pins: Django 2.0.13, grappelli 2.11.2, photologue 3.8.1 and sortedm2m 1.5.0.
Python stays at 3.7.

Two removals the plan did not list were in the tests, not the application:
direct assignment to ``user_permissions`` and the loader's ``load_template_source``.
ExifRead stays at 2.1.2 because photologue 3.8.1 only requires that version.

Checks
------

This section is for reviewers. It records the commands the branch ran and their results.

Run these commands from the repository root::

    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 dev/kasvimuseo app build
    podman build -t kasvimuseo-stage11-prod -f Dockerfile .
    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 KASVIMUSEO_PG_PORT=5711 KASVIMUSEO_DB_NAME=stage11 dev/kasvimuseo app test
    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 KASVIMUSEO_PG_PORT=5711 KASVIMUSEO_DB_NAME=stage11 dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
    KASVIMUSEO_IMAGE=kasvimuseo-dev-stage11 KASVIMUSEO_PG_PORT=5711 KASVIMUSEO_DB_NAME=stage11 dev/kasvimuseo app manage makemigrations --check --dry-run kasvimuseo --settings=ylaneenkasvit.test_settings
    dev/kasvimuseo docs

Results on 2026-09-15:

* The suite passed 531 tests in 22 seconds. The 10 remaining warnings are Python and Pillow deprecations inside Django and photologue.
* Both images report Django 2.0.13, grappelli 2.11.2, photologue 3.8.1, sortedm2m 1.5.0 and Python 3.7.17.
* ``check`` found no issues. ``makemigrations --check`` found no change in ``kasvimuseo``. photologue 3.8.1 ships the same ten migrations as 3.7.
* The branch regenerated the locks with issue 077's ``pip-compile`` command inside ``kasvimuseo-077-dev``.

Staging deployment
------------------

This section is for runtime maintainers. It records where Stage 11 ran and what the deployment proved.

The maintainer rebooted the staging host, and Stage 11 deployed to it on 2026-09-20.
The host is ``kasvimuseo-staging.vempai.men``, the Debian 10 target of the issue 070 rehearsals.
A first run on 2026-09-18 met the host unreachable and used a container instead; "The container substitute" below keeps that recipe.

The host ran Stage 6 before this deployment.
It served Django 1.8.19, grappelli 2.7.3, photologue 3.4.1, sortedm2m 1.1.1 and Pillow 6.2.2.
uWSGI loaded the ``python27`` plugin against a Python 2.7 user-site install.
So this one deployment carried the host through Stage 10's interpreter change as well as Stage 11.

Build the candidate archive, copy it to the host, and deploy it::

    podman run --rm -v "$PWD:/src" -w /src kasvimuseo-dev-stage11 python setup.py sdist --dist-dir .dev/staging
    scp .dev/staging/ylaneenkasvit-0.2.1.dev0.tar.gz kasvimuseo@<host>:/home/kasvimuseo/
    ansible-playbook -i ansible/hosts.staging -e @ansible/vars/staging.yml \
      --tags python,code,static,uwsgi \
      -e app_package=/home/kasvimuseo/ylaneenkasvit-0.2.1.dev0.tar.gz \
      --become-password-file .dev/rehearsal/become-pass ansible/install.yaml

Back up the database and ``uwsgi.ini`` first. The play installs the new environment beside the old one, and the database migration is the step that does not reverse itself.

Results on 2026-09-20:

* The play reported ``ok=17 changed=10 failed=0``.
* The host now runs Django 2.0.13, grappelli 2.11.2, photologue 3.8.1, sortedm2m 1.5.0, Pillow 9.5.0 and psycopg2-binary 2.8.6.
* uWSGI loads the ``python3`` plugin against ``/home/kasvimuseo/venv-python3.7``, which reports Python 3.7.3.
* ``migrate`` applied the 17 migrations Stages 7 to 11 had added, and left 29 applied and none pending.
* The data came through unchanged: 156 species, 311 observations and 137 photos, before and after.
* ``check --deploy`` reported no error. Its two warnings are the project's own ``SAMEORIGIN`` frame policy and the staging key.
* The three columns this issue rewrote render real markup, not escaped text. The admin shows ``(15cm,15cm)<br>15×15cm``, a link to ``/kasvimuseo/planted-observation/1291/`` and a link to ``/kasvimuseo/map/22/``.
* Five admin pages answered 200 for a logged-in superuser, including photologue's own list.
* The species list answered 200 with 55 KB, a species page rendered Finnish text, and the gallery and static host answered 200.
* HSTS still answers ``max-age=300``, the staging value.
* The candidate archive's SHA-256 is ``e76a7f065249424ebda39b011f0e8b9eebf4bacee19f9c561b9c4a8775b0e53f``.

Two things stayed out of the run.
nginx and certbot keep their 2026-08-09 configuration, because this change needs neither.
The media tree holds 20 KB and no photographs, as it did before, so no page here proves an image.

The rollback is the backup this deployment took, ``/root/stage11-backup-20260920-054939.sql``, and the previous ``uwsgi.ini`` beside it.

The container substitute
~~~~~~~~~~~~~~~~~~~~~~~~

Use this when the staging host does not answer, as it did not on 2026-09-18.
Stage 10 used the same substitute for :doc:`077-python-3-runtime-needs-a-rehearsed-transition`.

Start a Debian 10 container and deploy the same archive into it::

    podman run -d --name kasvimuseo-staging-s11 -v "$PWD/.dev/staging:/rehearsal" kasvimuseo-077-ansible-host /sbin/init
    ansible-playbook -i .dev/staging/hosts.container --tags python,code,static,database,uwsgi \
      -e app_package=/rehearsal/ylaneenkasvit-0.2.1.dev0.tar.gz ansible/install.yaml

The inventory names the ``containers.podman.podman`` connection and ``/usr/bin/python3.7``.
The image lacks three things the play needs.
Give the application user passwordless ``sudo``.
Install ``python3-psycopg2`` for Ansible's PostgreSQL modules.
Install ``acl`` so Ansible can become the ``postgres`` user.
Start the container with ``/sbin/init``, because the uWSGI role calls ``systemctl``.

That run, on 2026-09-18, installed the same stack on Debian 10.13 and Python 3.7.3.
It applied 29 migrations to an empty database, and its uWSGI service answered ``/admin/login/`` and ``/kasvimuseo/planted-species/`` with HTTP 200.
