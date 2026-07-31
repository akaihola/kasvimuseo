# -*- coding: utf-8 -*-
"""Tests for how the settings get ``ALLOWED_HOSTS`` (issue 026).

``hosts_from_env`` has no default, and that is the whole of it: with ``DEBUG``
off, an empty ``ALLOWED_HOSTS`` makes Django 1.5 raise ``SuspiciousOperation``
on every request, and ``['*']`` accepts a forged ``Host`` header. Either would
be a silent answer to a deployment that has not been told its host names, so
there is none -- which is as easy to undo by accident as 025's was, hence these.
"""

from __future__ import unicode_literals

import os

import pytest
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.test import RequestFactory

from ylaneenkasvit.common_settings import hosts_from_env

VARIABLE = 'KASVIMUSEO_TEST_ALLOWED_HOSTS'


@pytest.fixture
def unset_variable():
    os.environ.pop(VARIABLE, None)
    yield
    os.environ.pop(VARIABLE, None)


def test_one_host(unset_variable):
    os.environ[VARIABLE] = 'kasvit.example.com'
    assert hosts_from_env(VARIABLE) == ['kasvit.example.com']


def test_several_hosts_are_comma_separated(unset_variable):
    os.environ[VARIABLE] = 'kasvit.example.com, www.kasvit.example.com'
    assert hosts_from_env(VARIABLE) == ['kasvit.example.com',
                                        'www.kasvit.example.com']


def test_hosts_from_env_has_no_default(unset_variable):
    with pytest.raises(ImproperlyConfigured):
        hosts_from_env(VARIABLE)


def test_hosts_from_env_names_the_missing_variable(unset_variable):
    with pytest.raises(ImproperlyConfigured) as error:
        hosts_from_env(VARIABLE)
    assert VARIABLE in str(error.value)


def test_an_empty_value_is_not_a_deployment(unset_variable):
    """A variable set to nothing is the same mistake as not setting it.

    It would otherwise produce ``[]`` -- the state issue 026 is about, arrived
    at through the mechanism meant to prevent it.
    """
    os.environ[VARIABLE] = '  ,  '
    assert hosts_from_env(VARIABLE) == []


def test_a_forged_host_header_is_rejected(settings):
    """What ``ALLOWED_HOSTS`` is for, through Django's own check.

    Both conditions have to be set up, and neither holds by default here.
    ``DEBUG`` is on in the development image (``dev/Containerfile``) and Django
    1.5 consults the list only when it is off; and ``setup_test_environment``
    replaces ``ALLOWED_HOSTS`` with ``['*']`` for the whole run
    (``django/test/utils.py``), so what the settings module says is not what a
    test sees. Named here, they pin the behaviour production gets from the list
    Ansible supplies -- an unnamed host is refused, rather than served.
    """
    settings.DEBUG = False
    settings.ALLOWED_HOSTS = ['kasvit.example.com']
    with pytest.raises(SuspiciousOperation):
        RequestFactory(HTTP_HOST='evil.example.com').get('/').get_host()


def test_a_named_host_is_accepted(settings):
    settings.DEBUG = False
    settings.ALLOWED_HOSTS = ['kasvit.example.com']
    request = RequestFactory(HTTP_HOST='kasvit.example.com').get('/')
    assert request.get_host() == 'kasvit.example.com'
