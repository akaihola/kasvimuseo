=======================================================================
Issue 040: Django ships no translations, so the admin chrome is English
=======================================================================

:Status: Fixed
:Severity: Medium
:Area: packaging / i18n
:Reported: 2026-07-28
:Source: Dashboard walkthrough, branch ``dashboard-usability``
:Evidence: kasvimuseo/tests/test_admin.py -- ``test_admin_chrome_is_finnish``
    and ``test_submit_row_is_finnish`` now pin the fixed behaviour. They are
    the only assertions in the suite about a string this repository does not
    translate itself, and both fail against an image built before the fix
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- option 3 was to wait for the upgrade to retire Django 1.5
    044 -- the submit row, where one button translated and two did not
:Decision: Option 1 -- move the stray tree back into the package, in
    ``dev/Containerfile`` where it is astray, and assert the same property in
    the production ``Dockerfile``, which measurement showed was never affected
:Resolution: Fixed in cdb763b.

Problem
=======

``LANGUAGE_CODE`` is ``fi`` and the project translates its own strings, but
every string Django itself provides renders in English. On the admin front
page that is the ``Site administration`` heading, the ``Add`` and ``Change``
links on every model row, and the ``Groups`` and ``Users`` model names --
next to ``Kasvilajit``, ``Penkit``, ``Raportit ja työkalut`` and the rest in
Finnish.

The cause is not configuration. Django 1.5.1's ``setup.py`` lists its
non-Python files -- locale catalogs, fixtures, ``project_template``,
``contrib/admin/bin`` -- in ``data_files`` rather than ``package_data``.
Modern pip builds a wheel from that sdist, and a wheel installs ``data_files``
relative to the install prefix instead of into the package. In the dev image::

    /usr/local/lib/python2.7/site-packages/django/conf/locale/fi/  formats.py only
    /usr/local/django/conf/locale/fi/LC_MESSAGES/django.mo         14.2 kB, unreachable

``django/contrib/admin/locale/`` does not exist under ``site-packages`` at all;
its 2571 data files, Finnish included, all landed under ``/usr/local/django/``.
``gettext`` only looks inside the package, so the catalogs are installed but
never loaded.

Both images are affected: ``dev/Containerfile`` and the production
``Dockerfile`` install from ``requirements/production.txt`` the same way, and
the production build then copies ``/install`` (which contains the same stray
``django/`` tree) to ``/usr/local``.

That last paragraph is wrong, and fixing this is what showed it: the two images
do **not** install the same way, and only the development one is affected. See
"Decision" below for what was measured and where the difference comes from.

photologue's model names -- ``Galleries``, ``Photos`` -- are English for a
different reason: the installed photologue (2.6.1) ships catalogs for fifteen
languages, none of them Finnish.

Impact
======

Cosmetic but constant, and it lands on the page the application opens on. The
users are Finnish-speaking gardeners, and the admin is the whole application:
there is no separate front end to log into. Half-translated chrome is worse
than either extreme, because ``Add``/``Change`` sit on the same row as the
Finnish model names.

The submit row of any change form shows the same seam inside a single row of
buttons: ``Tallenna``, ``Save and add another``, ``Save and continue editing``.
``kasvimuseo/locale/fi/LC_MESSAGES/django.po`` carries a ``Save`` msgid of its
own -- the project catalog *is* loaded, so that one button translates -- and
has no entry for the two longer labels, which fall back to Django's unreachable
catalog and stay English. Filling in those two msgids in the project catalog
would cover the strings that matter most without moving anything. Issue 044 is
about the same three buttons.

Options
=======

1. Move the stray tree back where ``gettext`` looks, in both image
   definitions -- one line after the ``pip install``::

       cp -a /usr/local/django/. \
             /usr/local/lib/python2.7/site-packages/django/

   Cheapest, and it also restores the fixtures and ``project_template`` that
   went astray with the catalogs. It has to be repeated in the production
   ``Dockerfile``, where the copy has to happen in the ``builder`` stage or
   against ``/install``.

2. ``pip install --no-binary django``, which makes pip run the sdist's
   ``setup.py install`` and place the data files correctly. One flag, but it
   applies to the whole requirements file unless it is split.

3. Do nothing until the upgrade plan retires Django 1.5. Modern Django ships
   its catalogs as package data, so this fixes itself at that point -- see
   issue 036 for how far away that is.

Whatever is chosen, ``Galleries``/``Photos`` still needs a decision of its own:
either translate the two msgids in a project-level catalog or leave photologue
in English.

Decision
========

Option 1, and only ``dev/Containerfile`` actually needed it.

Option 2 was rejected on blast radius: ``--no-binary`` applies to the whole
requirements file unless it is split, and with three URL dependencies in there
(031) and the build ceilings in 028-030, forcing source builds for every pinned
package risks the image for a cosmetic fix. Option 3 was rejected because 036 is
not close, and this is on the page the application opens on.

**Only the development image was affected**, which is not what this file said
when it was written. Django 1.5.1's ``setup.py`` redirects the ``data`` install
scheme to ``purelib``::

    if len(sys.argv) >= 2 and sys.argv[1] == 'install':
        for scheme in INSTALL_SCHEMES.values():
            scheme['data'] = scheme['purelib']

so its ``data_files`` do land inside the package -- but only when pip runs
``setup.py install``. ``dev/Containerfile`` lets pip build a wheel, which never
runs that code, so the tree ends up in ``/usr/local/django``. The production
``Dockerfile`` passes ``--install-option="--prefix=/install"``, and that option
makes pip take the legacy ``setup.py install`` path, so the catalogs are already
in ``/install/lib/python2.7/site-packages/django/`` and there is nothing to
move. Measured, not reasoned: a first version of the fix that required
``/install/django`` to exist failed the builder stage with
``issue 040: expected /install/django/conf/locale to exist``, and
``find / -name django.mo -path '*fi*'`` in that stage lists them all under
``site-packages``.

Both images therefore carry the same step, in the shape the measurement asked
for rather than the one proposed above: move ``$prefix/django`` into the package
if it is there, then **assert** that ``conf/locale/fi`` and
``contrib/admin/locale/fi`` are readable inside the package and fail the build
if they are not. In the production ``Dockerfile`` it sits in the ``builder``
stage, before ``COPY --from=builder /install /usr/local``. That way neither
image can silently go back to an English admin: the dev image is fixed, the
production image is pinned to the behaviour it already has, and if pip's
handling of ``--install-option`` changes -- it is deprecated -- the copy simply
starts doing the work there too.

photologue's ``Galleries``/``Photos`` are **deliberately left in English**.
They are the only two English strings left on the front page, and they have a
different cause: photologue ships no ``fi`` catalog, so there is nothing to
make reachable. Translating them means adding ``galleries`` and ``photos``
msgids that occur nowhere in this repository's own source, and the next
``makemessages`` run over ``kasvimuseo`` or ``ylaneenkasvit`` would mark them
obsolete and drop them again. Doing it properly means a ``LOCALE_PATHS``
catalog for third-party strings, which is a change to the settings and a new
place to maintain -- out of scope for a packaging fix, and worth its own issue
if the two words are judged to matter. The dashboard module *titles* above them
("Kuvat", "Kuvagalleriat") are this project's strings and already Finnish.

Resolution
==========

``dev/Containerfile`` and ``Dockerfile`` each gained the step described above,
and ``kasvimuseo/tests/test_admin.py`` gained the first two assertions in the
suite about strings this repository does not translate itself:
``test_admin_chrome_is_finnish`` (the ``<h1>Sivuston ylläpito</h1>`` heading and
the ``Lisää``/``Muokkaa`` links, plus no ``Site administration`` anywhere) and
``test_submit_row_is_finnish``. Both pass against a rebuilt dev image and both
fail against an image built before the fix, which is what makes them evidence.
Commit cdb763b.

On the rebuilt image the admin front page is Finnish throughout: ``Sivuston
ylläpito``, ``Lisää``/``Muokkaa`` on every model row, ``Ryhmät``. Two English
strings remain, for two reasons that are not this one:

* ``Galleries`` and ``Photos``, ruled on above.
* ``Users``. This is a Django 1.5 bug, not a missing catalog: ``AbstractUser``
  declares ``verbose_name_plural = _('users')``, but ``class User`` overrides
  ``Meta`` without inheriting ``AbstractUser.Meta``, so ``Options`` derives the
  name from the class instead and ``User._meta.verbose_name_plural`` is
  ``string_concat('user', 's')`` rather than a translatable msgid. ``_('users')``
  on its own returns ``käyttäjät`` on the fixed image. Django 1.6 fixed it with
  ``class Meta(AbstractUser.Meta)``, so this one really does go away with the
  upgrade (036).

The submit row needed no project-level msgids, which answers the question this
file left open. Django's own catalog supplies ``Tallenna ja lisää toinen`` and
``Tallenna välillä ja jatka muokkaamista`` as soon as it is reachable, and the
first button still reads ``Tallenna`` rather than Django's ``Tallenna ja
poistu`` because the project catalog's own ``Save`` msgid outranks it. Issue 044
quotes the two English labels in its report; they are Finnish from now on, while
what 044 is about -- the row not arriving at all -- is untouched.

See also
========

Issue 036 (the runtime stack is end of life), ``docs/upgrade-plan.rst``.
