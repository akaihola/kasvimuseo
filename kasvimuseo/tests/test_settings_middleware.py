# -*- coding: utf-8 -*-
"""Tests for the explicit middleware list (issue 019).

``common_settings`` used to define no ``MIDDLEWARE_CLASSES`` at all, leaving the
site on the one in ``django.conf.global_settings`` -- which Django 2.0 removes,
so the project would have started with no middleware and said nothing. The list
is now written out, and this pins the two things that matter about it: that
writing it out changed nothing today, and that it is still the 1.5 default
rather than something that drifted.

The second assertion is expected to be *deliberately* changed, not to keep
passing for ever: from Stage 5 of ``docs/upgrade-plan.rst`` onwards the list
grows entries Django's own default does not have, and at Stage 8 it is renamed
to ``MIDDLEWARE``.
"""

from __future__ import unicode_literals

from django.conf import global_settings, settings


def test_middleware_is_the_installed_django_default():
    assert tuple(settings.MIDDLEWARE_CLASSES) == tuple(
        global_settings.MIDDLEWARE_CLASSES)


def test_middleware_is_defined_by_the_project_not_inherited():
    from ylaneenkasvit import common_settings

    assert tuple(common_settings.MIDDLEWARE_CLASSES) == tuple(
        global_settings.MIDDLEWARE_CLASSES)
