# -*- coding: utf-8 -*-
"""Sphinx configuration.

This file runs on the host's Python 3, never inside the application's Python 2.7
container, and nothing here imports the application. See
``docs/issues/038-no-rendered-documentation.rst`` for why, and for the points in
``docs/upgrade-plan.rst`` at which each workaround can be dropped.
"""

import os
import sys

# The issue-register extension lives beside this file rather than in a package:
# nothing installs it, and docs/issues/next.rst is the only thing that uses it.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_ext'))

project = 'Kasvimuseo'
copyright = 'Antti Kaihola'
author = 'Antti Kaihola'
# Kept in step with setup.py by hand; setup.py cannot be imported here.
release = '0.2.1.dev0'

extensions = [
    # Order matters: viewcode must be loaded before autoapi, or autoapi never
    # hands it the parsed source and the "[source]" links silently do not
    # appear. Nothing warns about this.
    'sphinx.ext.viewcode',
    'autoapi.extension',
    # Builds docs/issues/next.rst and the ranking tables in docs/issues/index.rst
    # from the issue files' own docinfo fields, and fails the build when the
    # ranking and the files disagree. See docs/_ext/issue_register.py.
    'sphinx_issue_register',
]

exclude_patterns = ['_build']

# -- API reference ----------------------------------------------------------
#
# sphinx-autoapi rather than sphinx.ext.autodoc: autodoc imports every module,
# which needs a working Django 1.5 environment on Python 2.7, where modern
# Sphinx cannot run. autoapi parses the source instead.
autoapi_dirs = ['../kasvimuseo', '../ylaneenkasvit']
autoapi_root = 'api'
autoapi_ignore = [
    # South migrations are noise in an API reference, and
    # 0011_extract_lighting.py additionally uses the Python 2 ``ur''`` prefix,
    # which no Python 3 parser accepts.
    '*/migrations/*',
    '*/tests/*',
    '*/local_settings*.py',
]
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
]
# Generated .rst is scratch: build it, use it, delete it. Nothing lands in git.
autoapi_keep_files = False
# api.rst places the generated pages in the tree by hand, with an explanation.
autoapi_add_toctree_entry = False

suppress_warnings = [
    # autoapi cannot follow ``from django.utils.dates import MONTHS`` into a
    # package it is not pointed at. Expected, and not something to fix here.
    'autoapi.python_import_resolution',
]

# ``models.py`` defines get_next_observation_extid and then rebinds the name to
# lazy(get_next_observation_extid, unicode), so autoapi sees both a function and
# a module attribute under one name and warns about the duplicate. The function
# is the one worth documenting; dropping the attribute leaves the build with no
# warnings at all, which is what lets dev/docs-build run with -W and so notice
# the day someone's edit breaks a page.
_LAZY_REBINDINGS = {'kasvimuseo.models.get_next_observation_extid'}


def _skip_lazy_rebinding(app, what, name, obj, skip, options):
    if what == 'data' and name in _LAZY_REBINDINGS:
        return True
    return skip


def setup(app):
    app.connect('autoapi-skip-member', _skip_lazy_rebinding)

# -- HTML output ------------------------------------------------------------

html_theme = 'furo'
html_title = 'Kasvimuseo'
