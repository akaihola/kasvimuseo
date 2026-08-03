# -*- coding: utf-8 -*-
"""Tests for the development login route (issue 068).

Two halves, and the second is the one that matters. That
``/dev-login/akaihola/`` logs akaihola in is a three-line view. That the route
exists nowhere but on a development server is the whole reason the view is
allowed to exist, so it is asserted from both ends: the URLconf does not carry
it with ``DEV_LOGIN`` off, and the view refuses even when something has reached
it anyway.

``DEV_LOGIN`` is off in ``test_settings``, deliberately -- ``dev/kasvimuseo``
exports the variable to this container too, and a suite whose URLconf depends
on the environment asserts nothing. The tests that need the route therefore
reload ``ylaneenkasvit.urls`` with the setting overridden and reload it back
afterwards; ``dev_login_urls`` is that fixture.
"""

from __future__ import unicode_literals

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import (Resolver404, clear_url_caches, resolve,
                                      reverse)
from django.http import Http404
from django.test.utils import override_settings
from django.utils.importlib import import_module
from django.utils.six.moves import reload_module

from ylaneenkasvit import common_settings
from ylaneenkasvit.dev_login import dev_login


@pytest.fixture
def user(db):
    """An account with an unusable password, which is the case in question.

    After ``dev/kasvimuseo db restore`` every local password is production's,
    known to nobody here (issues 049 and 050). Whatever this view does, it must
    not need one.
    """
    account = User.objects.create_user('akaihola', 'a@invalid')
    account.set_unusable_password()
    account.is_staff = True
    account.is_superuser = True
    account.save()
    return account


def load_urlconf():
    """Re-execute ``ylaneenkasvit/urls.py`` under the current settings."""
    urlconf = import_module(settings.ROOT_URLCONF)
    reload_module(urlconf)
    clear_url_caches()


@pytest.fixture
def dev_login_urls():
    """The URLconf a development server has, restored afterwards.

    The second ``load_urlconf`` is outside the ``with`` on purpose: it has to
    run with ``DEV_LOGIN`` back at its real value, or it would leave the route
    registered for every test that comes after this one.
    """
    with override_settings(DEV_LOGIN=True):
        load_urlconf()
        yield
    load_urlconf()


def test_the_route_logs_the_user_in(client, user, dev_login_urls):
    response = client.get(reverse('dev-login', args=[user.username]))

    assert response.status_code == 302
    assert response['Location'].endswith('/admin/')
    assert client.session['_auth_user_id'] == user.pk


def test_the_admin_is_open_afterwards(client, user, dev_login_urls):
    """The point of the whole thing: the next request is a logged-in one."""
    client.get('/dev-login/{0}/'.format(user.username))

    response = client.get('/admin/')

    assert response.status_code == 200
    assert 'id_username' not in response.content.decode('utf-8')


def test_an_unknown_user_is_a_404(client, db, dev_login_urls):
    assert client.get('/dev-login/eialkuunkaan/').status_code == 404


def test_an_inactive_user_is_a_404(client, user, dev_login_urls):
    """``login`` does not check; the form's rejection is in the backend."""
    user.is_active = False
    user.save()

    response = client.get('/dev-login/{0}/'.format(user.username))

    assert response.status_code == 404
    assert '_auth_user_id' not in client.session


def test_the_route_is_absent_without_the_setting(client, db):
    """The suite's own settings are the ones a deployment has."""
    assert settings.DEV_LOGIN is False
    assert client.get('/dev-login/akaihola/').status_code == 404
    with pytest.raises(Resolver404):
        resolve('/dev-login/akaihola/')


def test_the_view_refuses_without_the_setting(rf, user):
    """The second gate, for a caller that did not come through the URLconf."""
    with pytest.raises(Http404):
        dev_login(rf.get('/dev-login/akaihola/'), user.username)


@pytest.fixture
def reloadable_common_settings():
    """``common_settings`` re-executed, and put back as it was afterwards.

    ``test_settings_cookie_security`` reads production values off this same
    module object, so leaving it holding a value this test invented would make
    that suite's answer depend on the order the two ran in.
    """
    yield
    reload_module(common_settings)


def test_the_setting_is_off_where_nothing_asks_for_it(
        monkeypatch, reloadable_common_settings):
    """``common_settings`` is what a deployment loads, and it reads one thing.

    Asserted against the module rather than through ``django.conf.settings``,
    which here is ``test_settings`` and turns the value off by hand: that
    override is what keeps the suite honest, not what keeps production safe.
    """
    monkeypatch.delenv(str('KASVIMUSEO_DEV_LOGIN'), raising=False)
    reload_module(common_settings)

    assert common_settings.DEV_LOGIN is False

    monkeypatch.setenv(str('KASVIMUSEO_DEV_LOGIN'), str('1'))
    reload_module(common_settings)

    assert common_settings.DEV_LOGIN is True
