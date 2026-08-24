# -*- coding: utf-8 -*-
"""Tests for the explicit middleware list (issue 019).

``common_settings`` used to define no ``MIDDLEWARE_CLASSES`` at all, leaving the
site on the one in ``django.conf.global_settings`` -- which Django 2.0 removes,
so the project would have started with no middleware and said nothing. The list
is now written out, and this pins the two things that matter about it: that
writing it out changed nothing today, and that it is still the 1.5 default
rather than something that drifted.

The second assertion is expected to be *deliberately* changed, not to keep
passing for ever: the list grows entries Django's own default does not have.

Three deliberate changes have happened so far. At Stage 8 of
``docs/upgrade-plan.rst`` the setting became ``MIDDLEWARE``: Django 1.10
reads the new name, and 2.0 stops reading the old one. ``XFrameOptionsMiddleware`` was
added for issue 059. And at upgrade plan Stage 5 the comparison to the
installed ``global_settings`` ended: Django 1.7 cut its own default down to
``CommonMiddleware`` and ``CsrfViewMiddleware``, because its project template
started writing the list out -- the same move issue 019 made here. The list
below is therefore a literal now: the Django 1.5 default this project has
always run on, plus the one addition. That an upgrade changed Django's default
and this application kept its behaviour is 019 working as intended.
"""

from __future__ import unicode_literals

from django.conf import settings

EXPECTED = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Added deliberately; not in the 1.5 default (issue 059).
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


def test_middleware_is_the_django_15_default_plus_clickjacking():
    assert tuple(settings.MIDDLEWARE) == EXPECTED


def test_middleware_is_defined_by_the_project_not_inherited():
    from ylaneenkasvit import common_settings

    assert tuple(common_settings.MIDDLEWARE) == EXPECTED
