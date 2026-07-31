# -*- coding: utf-8 -*-
"""Tests for ``TEMPLATE_DIRS`` (issue 024).

``common_settings`` used to name photologue's template directory by literal
path, ``../lib/python2.7/site-packages/photologue/templates``, which encoded
the interpreter version in a settings file and would silently resolve to
nothing on Python 3.7. It was also unnecessary, and in the container it had
already stopped resolving: the dependencies live in the image and the working
copy is mounted at ``/src``, which has no ``lib/``.

The entry is gone, and these pin why deleting it was safe: the app template
loader is active, and photologue's templates come from inside the installed
package. ``test_project_urls.py`` renders the gallery pages themselves; the
last test here is the one that would notice if they started being found
somewhere other than the package.
"""

from __future__ import unicode_literals

import os

import photologue
import pytest
from django.conf import global_settings, settings
from django.core.urlresolvers import reverse
from django.template.loaders.app_directories import Loader

APP_LOADER = 'django.template.loaders.app_directories.Loader'


def test_template_dirs_names_only_the_projects_own_templates():
    from ylaneenkasvit import common_settings

    assert tuple(settings.TEMPLATE_DIRS) == (common_settings.here('templates'),)


def test_no_template_dir_reaches_into_site_packages():
    for directory in settings.TEMPLATE_DIRS:
        assert 'site-packages' not in directory
        assert 'python2.7' not in directory


def test_the_app_template_loader_is_active():
    """Unset here, so this is Django's own default rather than a project list."""
    from ylaneenkasvit import common_settings

    assert not hasattr(common_settings, 'TEMPLATE_LOADERS')
    assert APP_LOADER in global_settings.TEMPLATE_LOADERS
    assert APP_LOADER in settings.TEMPLATE_LOADERS


def test_photologue_templates_are_found_inside_the_installed_package():
    # The loader itself rather than ``django.template.loader.find_template``,
    # which reports the file a template came from only under ``TEMPLATE_DEBUG``
    # -- and the file is the whole point here.
    source, filename = Loader().load_template_source(
        'photologue/gallery_archive.html')

    assert filename.startswith(os.path.dirname(photologue.__file__) + os.sep)


@pytest.mark.django_db
def test_the_gallery_index_renders_photologues_own_template(client):
    response = client.get(reverse('pl-gallery-archive'))

    assert response.status_code == 200
    assert 'photologue/gallery_archive.html' in [t.name
                                                 for t in response.templates]
