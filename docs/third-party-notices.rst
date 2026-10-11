===================
Third-party notices
===================

This page is for the maintainer who copies a file from another project, and
for the reviewer who checks that a release carries the required notices. It
lists every vendored component: its origin, its version, its license, and the
file that holds the notice.

Before you copy a file from another project, add a row to the table below and
put the upstream license text beside the file. Keep the author names and the
e-mail addresses inside the notice files. They are upstream attribution, not
personal data of this project, so the personal-information cleanup (task 3)
leaves them in place.

The inventory
=============

The table lists the path in this repository, the upstream project, the exact
upstream version, the license, and the notice file.
``kasvimuseo/tests/test_third_party_notices.py`` checks that every row names a
file that exists and has its notice.

.. list-table::
   :header-rows: 1
   :widths: 30 25 10 10 25

   * - Path
     - Upstream
     - Version
     - License
     - Notice file
   * - ``jqm/``
     - `django-jqm <https://github.com/akaihola/django-jqm>`_ by Mike C.
       Fletcher; a personal fork of the Launchpad project
     - ``1.1.0.2``
     - MIT
     - ``jqm/LICENSE``
   * - ``kasvimuseo/static/js/kasvimuseo/fitty.min.js``
     - `fitty <https://github.com/rikschennink/fitty>`_ by Rik Schennink
     - ``2.2.5``
     - MIT
     - ``kasvimuseo/static/js/kasvimuseo/fitty.min.js.LICENSE.txt``
   * - ``kasvimuseo/static/grappelli/jquery/i18n/ui.datepicker-fi.js``
     - `jQuery UI <https://github.com/jquery/jquery-ui>`_,
       ``ui/i18n/jquery.ui.datepicker-fi.js`` by Harri Kilpiö
     - ``1.10.3``
     - MIT
     - ``kasvimuseo/static/grappelli/jquery/i18n/ui.datepicker-fi.js.LICENSE.txt``
   * - ``browser_tests/vendor/vue.min.js``
     - `Vue.js <https://github.com/vuejs/vue>`_ by Evan You
     - ``2.6.14``
     - MIT
     - ``browser_tests/vendor/vue.min.js.LICENSE.txt``
   * - ``browser_tests/vendor/axios.min.js``
     - `axios <https://github.com/axios/axios>`_ by Matt Zabriskie and
       collaborators
     - ``1.7.9``
     - MIT
     - ``browser_tests/vendor/axios.min.js.LICENSE.txt``
   * - ``browser_tests/vendor/sanitize.min.css``
     - `sanitize.css <https://github.com/csstools/sanitize.css>`_ by
       Jonathan Neal
     - ``2.0.0``
     - CC0 1.0
     - ``browser_tests/vendor/sanitize.min.css.LICENSE.txt``

What the check on 2026-10-10 found
==================================

Task 7 compared every copy with the file at the upstream version named above.

* ``jqm/``: six templates and two static files are identical to the
  ``1.1.0.2`` archive, except ``templates/jqm/simple.html``. That template
  submits the logout link as a form with a CSRF token (commit ``0fac221``).
  The archive has no license text; ``jqm/LICENSE`` says so and supplies the
  MIT text. The copy keeps the Launchpad origin in ``jqm/README.rst``.
* ``fitty.min.js``: identical to ``dist/fitty.min.js`` at tag ``2.2.5``. The
  file keeps its upstream header with the copyright line.
* ``ui.datepicker-fi.js``: the jQuery UI ``1.10.3`` file with two additions.
  The header names the author, the source and the date, and a comment
  explains why Grappelli needs the file. The code is unchanged.
* ``vue.min.js``: identical to ``dist/vue.min.js`` of the ``vue@2.6.14`` npm
  package. The file keeps its upstream header.
* ``axios.min.js``: identical to ``dist/axios.min.js`` of the ``axios@1.7.9``
  npm package. The upstream build has no header, so the notice file is the
  only attribution.
* ``sanitize.min.css``: identical to ``dist/sanitize.css`` at tag ``v2.0.0``,
  which is the minified build upstream shipped. The CDN file the page loads
  is a different build of the same version, with an MIT header. CC0 requires
  no notice; the copy keeps the upstream header anyway.

Where the notices travel
========================

The source distribution and the wheel carry ``jqm/LICENSE`` and both static
notice files: ``MANIFEST.in`` names ``jqm/LICENSE``, and the ``package_data``
globs in ``setup.py`` match the rest. ``dev/check-release-artifacts`` lists
the three files as required, and the production image build checks them
after ``pip install``. The ``browser_tests/vendor/`` copies never leave the
repository, so their notice files only need to exist beside them.

What is not vendored
====================

The pages still load jQuery, jQuery Mobile, Vue, axios and sanitize.css from
CDNs. A file a visitor's browser fetches is not a copy in this repository, so
it needs no notice here. ``jqm/README.rst`` explains the jQuery case.

Templates under ``ylaneenkasvit/templates/`` and ``kasvimuseo/templates/``
that start with ``{% extends %}`` override a Django or Grappelli template.
They contain this project's own markup only.
