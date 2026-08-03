# -*- coding: utf-8 -*-
"""The Finnish date picker grappelli asks for and does not ship.

Grappelli 2.5 -- upgrade plan Stage 3 -- renders an unconditional

    <script src="{% static 'grappelli/jquery/i18n/ui.datepicker-'
                 |add:LANGUAGE_CODE|add:'.js' %}">

into ``admin/base.html``, and the package contains exactly two of those files,
``de`` and ``fr``. ``LANGUAGE_CODE`` here is ``fi``, so before this project
supplied one every admin page fetched a 404 and the date picker on every
``DateField`` stayed English. The browser suite is what noticed, because it
asserts that a page produces no console errors.

The file lives in ``kasvimuseo/static/`` under grappelli's own name:
``kasvimuseo`` precedes ``grappelli`` in ``INSTALLED_APPS``, so the
app-directories finder returns this one and nothing is vendored or overridden.
That also makes it the kind of file that goes missing quietly -- it is a path
in ``setup.py``'s ``package_data``, one segment deeper than the globs there
used to reach -- which is what these tests are for. The production image
asserts the same thing at build time; this asserts it for the development
image and the suite.
"""

from __future__ import unicode_literals

import io

from django.conf import settings
from django.contrib.staticfiles import finders

DATEPICKER = 'grappelli/jquery/i18n/ui.datepicker-fi.js'


def test_the_static_finders_have_the_file_grappelli_asks_for():
    assert finders.find(DATEPICKER) is not None, (
        'grappelli renders a <script> for this on every admin page')


def test_it_is_this_projects_copy_rather_than_grappellis():
    """Grappelli ships no ``fi``, so a hit inside the package would mean the
    file had been patched into an installed dependency instead."""
    assert 'grappelli/static' not in finders.find(DATEPICKER)
    assert 'kasvimuseo' in finders.find(DATEPICKER)


def test_it_runs_under_grappellis_jquery_and_the_projects_date_format():
    """Two details copied from grappelli's own ``ui.datepicker-de.js``.

    The page's global ``jQuery`` is Django's; grappelli's is ``grp.jQuery``, so
    the wrong wrapper is a ``TypeError`` at load rather than a wrong month
    name. And the format is ``DATE_FORMAT``'s, not the Finnish locale's, which
    is what grappelli overrides it to per field anyway.
    """
    with io.open(finders.find(DATEPICKER), encoding='utf-8') as source:
        content = source.read()

    assert content.rstrip().endswith('})(grp.jQuery);')
    assert "dateFormat: 'yy-mm-dd'" in content
    assert settings.DATE_FORMAT == 'Y-m-d'


def test_the_language_that_names_it_is_still_finnish():
    """``LANGUAGE_CODE`` is what grappelli interpolates into the file name."""
    assert settings.LANGUAGE_CODE == 'fi'
