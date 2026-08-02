=============================================================================
Issue 058: The production image ships none of the project's own data files
=============================================================================

:Status: Fixed
:Severity: Medium
:Area: packaging / images
:Reported: 2026-08-01
:Source: Verifying Stage 1 of :doc:`../upgrade-plan`, which is why a page was
    rendered from the production ``Dockerfile`` image at all. Written into
    ``incoming.rst`` first, because what it needed before it was worth a
    number was an answer to "is this image deployed anywhere?"
:Evidence: The regression test is the ``RUN`` block in ``Dockerfile`` itself --
    six ``test -r`` calls over the files that reach the install only through
    ``MANIFEST.in``. Nothing in the pytest suite can see this defect: the suite
    runs against the working tree, where ``ylaneenkasvit/templates/base.html``
    is always there, so a test asserting it exists would pass against the
    broken image as loudly as against the fixed one. What the fault is a
    property of is the *build*, which is where the assertion is. Removing the
    ``COPY MANIFEST.in`` line and rebuilding fails the build on exactly that
    step, which is the check that the assertion is not decorative -- run,
    below
:Depends on: (none)
:Blocks: (none)
:Related: 040 -- the same class of fault, one dependency further out: files
    that are installed somewhere the loader does not look, or not at all,
    because of how a ``setup.py`` names them. Its assertion in this same
    ``Dockerfile`` is the idiom this one follows
    031 -- ``jqm``, the vendored ``django-jqm``, whose templates are in
    ``package_data`` explicitly and were therefore never affected
    027 -- the other change that made this image reproducible rather than
    dependent on what pip happened to resolve
    008 -- ``/photologue/gallery/``, the URL this was found on, for an
    unrelated reason
:Decision: Fix it, and record that nothing deploys this image. Both halves were checked rather than assumed. **Nothing deploys it**: ``ansible/install.yaml`` -- the only installer in this repository -- installs the application with ``pip install --user git+ssh://git@bitbucket.org/akaihola/kasvimuseo.git`` onto a Debian host and serves it with uWSGI behind nginx, so production builds from a git checkout, where ``MANIFEST.in`` sits beside ``setup.py`` and ``include_package_data`` works. ``.github/workflows/tests.yml`` is the only workflow, and it builds ``dev/Containerfile`` twice and this ``Dockerfile`` never; no registry is named anywhere in the tree. So this defect has no user today, which is why it is ``Medium`` and not ``High`` -- but it is not "a definition of a thing nobody runs" either, because the one thing this file is *for* is showing the application to somebody with no development checkout, and it did not do that. The repair is one ``COPY`` line, and the alternative -- name the same files a second time in ``setup.py``'s ``package_data``, so the image stops depending on ``MANIFEST.in`` -- was rejected: it would leave two lists of the same files to keep in step, and the list that ``pip install`` from the git URL already honours is ``MANIFEST.in``. What the image was missing was not the mechanism but the file.
:Resolution: acc8b9d -- ``COPY MANIFEST.in`` into the build context in ``Dockerfile``, plus a ``RUN`` block that fails the build if any of the six files it carries is not readable in the installed package. ``ylaneenkasvit/locale/`` and ``kasvimuseo/locale/`` were missing too, and are fixed by the same line; the assertion covers them.

Problem
=======

``Dockerfile`` builds the application into ``/install`` and copies that into
the runtime image. It copies four things into the build context it installs
from::

    COPY setup.py /kasvimuseo/setup.py
    COPY kasvimuseo /kasvimuseo/kasvimuseo
    COPY ylaneenkasvit /kasvimuseo/ylaneenkasvit
    COPY jqm /kasvimuseo/jqm
    RUN pip install --install-option="--prefix=/install" /kasvimuseo

``MANIFEST.in`` is not among them, and it is the only thing in this repository
that names the project's non-Python files other than ``kasvimuseo``'s and
``jqm``'s::

    recursive-include */locale *.po
    recursive-include */locale *.mo
    recursive-include ylaneenkasvit/templates *.html

``setup.py`` sets ``include_package_data=True``, which means "install whatever
the manifest lists, for every package", and it also names two packages'
directories explicitly in ``package_data``: ``kasvimuseo``'s ``static`` and
``templates``, and ``jqm``'s. Those two are globs evaluated against the source
tree and need no manifest, which is why they survived and everything else did
not.

The install path matters, and it turns out not to change the answer.
``pip install /kasvimuseo`` installs from a **directory**, not from an sdist,
and ``--install-option`` makes pip run ``setup.py install`` rather than build a
wheel. On that path setuptools regenerates the manifest from ``MANIFEST.in``
during ``egg_info`` -- and with no ``MANIFEST.in`` to read it produces the
default list, Python files only. ``build_py`` then installs, for each package,
the ``package_data`` globs plus whatever the manifest listed, and the second
of those is empty. The egg-info the image ships records it::

    $ podman run --rm kasvi-058-before sh -c 'grep -E "locale|ylaneenkasvit/templates" \
        /usr/local/lib/python2.7/site-packages/ylaneenkasvit-0.2.1.dev0-py2.7.egg-info/SOURCES.txt'
    $                                  # nothing, out of 85 lines

So the package installed with no ``templates/`` and no ``locale/`` at all::

    $ podman run --rm kasvi-058-before \
        find /usr/local/lib/python2.7/site-packages/ylaneenkasvit -type f | sort
    .../ylaneenkasvit/__init__.py
    .../ylaneenkasvit/common_settings.py
    .../ylaneenkasvit/dashboard.py
    ...                                # thirteen .py files and their .pyc, and nothing else

    $ podman run --rm kasvi-058-before sh -c \
        'ls /usr/local/lib/python2.7/site-packages/kasvimuseo/locale'
    ls: /usr/local/lib/python2.7/site-packages/kasvimuseo/locale: No such file or directory

``kasvimuseo/templates/`` **is** in that image, and ``jqm``'s templates and
static files are too. That is the shape of the fault: the two directories
``setup.py`` names by hand are there, and the three ``MANIFEST.in`` names are
not.

Impact
======

Two things, and the report only carried the first.

**Every page that extends** ``base.html`` **is a 500.** ``base.html``,
``404.html``, ``500.html`` and the one Grappelli dashboard override live in
``ylaneenkasvit/templates/``, and there is no ``TEMPLATE_DIRS`` entry pointing
anywhere else that has them -- they are found because ``ylaneenkasvit`` is an
installed application. Against a bootstrapped database, in the image as it was::

    $ for u in /admin/ /accounts/login/ /kasvimuseo/planted-species/ /photologue/gallery/; do
          curl -s -o /dev/null -w "%{http_code} $u\n" http://127.0.0.1:8058$u; done
    200 /admin/
    200 /accounts/login/
    200 /kasvimuseo/planted-species/
    500 /photologue/gallery/

and with ``KASVIMUSEO_DEBUG=1``::

    <title>TemplateDoesNotExist at /photologue/gallery/</title>

Three of those four answer 200 because they do not reach the missing file:
the admin and the login page extend Django's and Grappelli's own base
templates, and ``planted-species`` extends a ``kasvimuseo`` one -- from the
package whose templates ``setup.py`` names. The 404 and 500 pages are missing
as well, so an error in this image is an error rendering the error page.

**And the application speaks English**, which is issue 040 over again on this
project's own catalogs rather than on Django's. There is no ``LOCALE_PATHS``:
``ylaneenkasvit/locale/`` and ``kasvimuseo/locale/`` are loaded because both
are installed applications, and neither was in the image. Measured in each
image, with ``LANGUAGE_CODE = 'fi'`` in force::

    $ podman run --rm ... $img python -c "
    from django.utils import translation; translation.activate('fi')
    from django.utils.translation import ugettext as _
    for s in ['Reports and tools', 'Planted species', 'Create Species Sheets',
              'Basic information']:
        print('%-24s -> %s' % (s, _(s).encode('utf-8')))"

    == kasvi-058-before                 == kasvi-058-after
    Reports and tools     -> Reports and tools      -> Raportit ja työkalut
    Planted species       -> Planted species        -> Istutetut kasvit
    Create Species Sheets -> Create Species Sheets  -> Luo kasvilajien tietosivut
    Basic information     -> Basic information      -> Perustiedot

Those four strings are the admin dashboard's group headings, the mobile list's
title and an admin action -- the Finnish half of the page 040 was written
about. In this image 040's fix landed and this one undid more than it: after
cdb763b Django's own chrome is Finnish here, and the project's own strings were
the English ones.

**Nobody is served either page**, which is why this is ``Medium``. See
``Decision`` for what was read to establish that: production is an Ansible
install from a git checkout, and no workflow, script or playbook in this
repository builds or pushes this image.

**It is not the upgrade plan's doing.** ``kasvi-s02-prod``, built from
``master`` before this branch existed, has the same hole::

    $ podman run --rm kasvi-s02-prod sh -c \
        'ls /usr/local/lib/python2.7/site-packages/ylaneenkasvit/templates'
    ls: .../ylaneenkasvit/templates: No such file or directory

The three ``COPY`` lines and the ``MANIFEST.in`` they omit predate Stage 1,
Stage 2 and issue 031's ``COPY jqm``.

Fix
===

One line, and an assertion so it stays::

    COPY MANIFEST.in /kasvimuseo/MANIFEST.in

with the comment beside it saying what ``package_data`` covers and what only
this file covers, and after ``pip install``:

.. code-block:: docker

    RUN set -e; \
        site=/install/lib/python2.7/site-packages; \
        for f in ylaneenkasvit/templates/base.html \
                 ylaneenkasvit/templates/404.html \
                 ylaneenkasvit/templates/500.html \
                 ylaneenkasvit/templates/grappelli/dashboard/modules/link_list.html \
                 ylaneenkasvit/locale/fi/LC_MESSAGES/django.mo \
                 kasvimuseo/locale/fi/LC_MESSAGES/django.mo; do \
            test -r "$site/$f" || { \
                echo "issue 058: $site/$f is missing from the installed package." \
                     "MANIFEST.in is the only thing that puts it there, so check" \
                     "that it is still COPYed into /kasvimuseo above and still" \
                     "names this file" >&2; \
                exit 1; \
            }; \
        done

It is in the builder stage, beside the block issue 040 put there for Django's
catalogs, and it names one file per line ``MANIFEST.in`` carries rather than
just ``base.html``: the three patterns cover four kinds of file, and a manifest
that lost one of them would otherwise pass. A ``COPY`` reorganised later is
what this catches -- the class of change that put the defect here in the first
place.

Verification
============

**The package.** In the image built from ``Dockerfile`` after the change::

    $ podman run --rm kasvi-058-after sh -c \
        'ls /usr/local/lib/python2.7/site-packages/ylaneenkasvit/templates
         ls /usr/local/lib/python2.7/site-packages/ylaneenkasvit/templates/grappelli/dashboard/modules
         find /usr/local/lib/python2.7/site-packages/ylaneenkasvit/locale \
              /usr/local/lib/python2.7/site-packages/kasvimuseo/locale -type f'
    404.html
    500.html
    base.html
    grappelli
    link_list.html
    .../ylaneenkasvit/locale/fi/LC_MESSAGES/django.mo
    .../ylaneenkasvit/locale/fi/LC_MESSAGES/django.po
    .../kasvimuseo/locale/fi/LC_MESSAGES/django.mo
    .../kasvimuseo/locale/fi/LC_MESSAGES/django.po

**The pages**, on the same bootstrapped database the 500 above was measured
on, with the fixed image serving::

    200 /admin/
    200 /accounts/login/
    200 /kasvimuseo/planted-species/
    200 /photologue/gallery/

**The assertion.** ``grep -v '^COPY MANIFEST.in' Dockerfile`` into a second
file and building that fails, on the step it should::

    issue 058: /install/lib/python2.7/site-packages/ylaneenkasvit/templates/base.html
    is missing from the installed package. MANIFEST.in is the only thing that puts
    it there, so check that it is still COPYed into /kasvimuseo above and still
    names this file
    Error: building at STEP "RUN set -e; site=/install/..." : exit status 1

    $ echo $?
    1

Nothing else in the build was touched, so the two images differ by one ``COPY``
layer and one ``RUN``.

**The suites**, which this change cannot reach and which were run anyway:
``dev/kasvimuseo app test`` passes, 435 tests, and
``dev/kasvimuseo app browser-test`` passes, 29. Both use ``dev/Containerfile``,
which installs nothing -- it reads the working copy from a bind mount -- so
neither image definition's packaging is on their path.
``.github/workflows/tests.yml`` is unchanged and never builds this
``Dockerfile``; ``actionlint`` on it is clean.

What this does not fix
======================

The image still has no ``local_settings.py`` -- deliberately, and
``.containerignore`` keeps a developer's out of it -- so it needs
``KASVIMUSEO_SECRET_KEY``, ``KASVIMUSEO_DB_PASSWORD`` and
``KASVIMUSEO_ALLOWED_HOSTS`` in its environment and a PostgreSQL socket
mounted at ``/var/run/postgresql`` before it serves anything. That is what it
was always for, and ``README.rst`` does not describe it, because nothing in
this repository builds it as part of any workflow. Whether it should be
documented, given a ``dev/kasvimuseo`` subcommand, or deleted is a question
this issue does not answer; what it establishes is that the file now produces a
working application when it is built, which is the precondition for any of the
three.
