# -*- coding: utf-8 -*-
"""Tests for how the settings get their secrets (issue 025).

The point of ``secret_from_env`` is what it refuses to do: there is no default,
so a deployment that forgets a variable stops instead of signing cookies with a
value that is in this repository's history. That is easy to undo by accident --
one ``os.environ.get(name, something)`` -- so it is pinned here.
"""

from __future__ import unicode_literals

import os

import pytest
from django.core.exceptions import ImproperlyConfigured

from ylaneenkasvit.common_settings import secret_from_env

VARIABLE = 'KASVIMUSEO_TEST_SECRET_FROM_ENV'


@pytest.fixture
def unset_variable():
    os.environ.pop(VARIABLE, None)
    yield
    os.environ.pop(VARIABLE, None)


def test_secret_from_env_returns_the_value(unset_variable):
    os.environ[VARIABLE] = 'a value'
    assert secret_from_env(VARIABLE) == 'a value'


def test_secret_from_env_has_no_default(unset_variable):
    with pytest.raises(ImproperlyConfigured):
        secret_from_env(VARIABLE)


def test_secret_from_env_names_the_missing_variable(unset_variable):
    with pytest.raises(ImproperlyConfigured) as error:
        secret_from_env(VARIABLE)
    assert VARIABLE in str(error.value)
