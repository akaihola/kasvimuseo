# -*- coding: utf-8 -*-
"""Tests for the template configuration (issue 024, upgrade plan Stage 6).

``common_settings`` used to name photologue's template directory by literal
path, ``../lib/python2.7/site-packages/photologue/templates``, which encoded
the interpreter version in a settings file and would silently resolve to
nothing on Python 3.7. It was also unnecessary, and in the container it had
already stopped resolving: the dependencies live in the image and the working
copy is mounted at ``/src``, which has no ``lib/``.

The entry is gone, and these pin why deleting it was safe: the application
template loader is active, and photologue's templates come from inside the
installed package. Since Stage 6 the settings are one ``TEMPLATES`` entry, so
the directory list is its ``DIRS`` and the loader is its ``APP_DIRS``.
``test_project_urls.py`` renders the gallery pages themselves; the last test
here is the one that would notice if they started being found somewhere other
than the package.
"""

from __future__ import unicode_literals

import os

import photologue
import pytest
from django.conf import settings
from django.urls import reverse
from django.template import engines
from django.template.loaders.app_directories import Loader

APP_LOADER = 'django.template.loaders.app_directories.Loader'


def test_template_dirs_names_only_the_projects_own_templates():
    from ylaneenkasvit import common_settings

    assert settings.TEMPLATES[0]['DIRS'] == [common_settings.here('templates')]


def test_no_template_dir_reaches_into_site_packages():
    for directory in settings.TEMPLATES[0]['DIRS']:
        assert 'site-packages' not in directory
        assert 'python2.7' not in directory


def test_the_app_template_loader_is_active():
    """``APP_DIRS`` and no ``loaders`` override, so Django builds the same
    two loaders its 1.5 ``TEMPLATE_LOADERS`` default named."""
    assert settings.TEMPLATES[0]['APP_DIRS'] is True
    assert 'loaders' not in settings.TEMPLATES[0]['OPTIONS']
    loaded = ['{0.__module__}.{0.__name__}'.format(type(loader))
              for loader in engines['django'].engine.template_loaders]
    assert APP_LOADER in loaded


def test_photologue_templates_are_found_inside_the_installed_package():
    # The loader itself rather than the engine's ``find_template``, which
    # reports the file a template came from only under template debug mode
    # -- and the file is the whole point here.
    source, filename = Loader(engines['django'].engine).load_template_source(
        'photologue/gallery_archive.html')

    assert filename.startswith(os.path.dirname(photologue.__file__) + os.sep)


@pytest.mark.django_db
def test_the_gallery_index_renders_photologues_own_template(client):
    response = client.get(reverse('pl-gallery-archive'))

    assert response.status_code == 200
    assert 'photologue/gallery_archive.html' in [t.name
                                                 for t in response.templates]
