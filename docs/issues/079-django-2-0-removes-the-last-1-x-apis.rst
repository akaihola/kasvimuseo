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

The recorded staging host ``kasvimuseo-staging.vempai.men`` did not answer on 2026-09-18.
It refused ping and connections on ports 22, 80 and 443.
Hetzner Cloud still reported the server as running, and another server in the same location answered at once.
A reboot is the remedy, and this environment refuses to run one, so the host waits for the maintainer.
An isolated Debian 10 container supplied the target instead, as Stage 10 did for :doc:`077-python-3-runtime-needs-a-rehearsed-transition`.

Build the candidate archive and start the target::

    podman run --rm -v "$PWD:/src" -w /src kasvimuseo-dev-stage11 python setup.py sdist --dist-dir .dev/staging
    podman run -d --name kasvimuseo-staging-s11 -v "$PWD/.dev/staging:/rehearsal" kasvimuseo-077-ansible-host /sbin/init

Then deploy the archive with the repository's own play::

    ansible-playbook -i .dev/staging/hosts.container --tags python,code,static,database,uwsgi \
      -e app_package=/rehearsal/ylaneenkasvit-0.2.1.dev0.tar.gz ansible/install.yaml

The image lacks three things the play needs.
Give the application user passwordless ``sudo``.
Install ``python3-psycopg2`` for Ansible's PostgreSQL modules.
Install ``acl`` so Ansible can become the ``postgres`` user.

Results on 2026-09-18:

* The target reported Debian 10.13 and Python 3.7.3, an older release than the images' 3.7.17.
* The environment holds Django 2.0.13, grappelli 2.11.2, photologue 3.8.1, sortedm2m 1.5.0, Pillow 9.5.0 and psycopg2-binary 2.8.6.
* ``collectstatic`` wrote the static tree, and ``migrate`` applied 29 migrations to an empty database.
* ``check --deploy`` reported no error. It warned about the throwaway key's length and the project's frame policy.
* The uWSGI service started and answered ``/admin/login/`` and ``/kasvimuseo/planted-species/`` with HTTP 200.
* The run left out nginx and certbot. Both need a reachable host and real DNS.
* The candidate archive's SHA-256 is ``316af75251a66e2cd669476112d4f06cd7484cc8b3b7fbf98cc8eb3ca99e27a4``.
