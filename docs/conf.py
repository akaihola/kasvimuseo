# -*- coding: utf-8 -*-
"""Sphinx configuration.

This file runs on the host's Python 3, never inside the application's Python 2.7
container, and nothing here imports the application. See
``docs/issues/038-no-rendered-documentation.rst`` for why, and for the points in
``docs/upgrade-plan.rst`` at which each workaround can be dropped.
"""

project = 'Ylåneen kasvit'
copyright = 'Antti Kaihola'
author = 'Antti Kaihola'
# Kept in step with setup.py by hand; setup.py cannot be imported here.
release = '0.2.1.dev0'

extensions = [
    'autoapi.extension',
    'sphinx.ext.viewcode',
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

# -- HTML output ------------------------------------------------------------

html_theme = 'furo'
html_title = 'Ylåneen kasvit'
