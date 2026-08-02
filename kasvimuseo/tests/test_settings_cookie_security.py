# -*- coding: utf-8 -*-
"""Tests for the cookie and framing settings (issue 059).

Three things, and the interesting ones are behavioural rather than a reading of
``settings``:

* the session and CSRF cookies are marked ``Secure`` under the settings
  production loads, so a request that reaches ``http://`` before nginx's 301
  carries no cookie to leak;
* development and the suite are *not*, because both are plain HTTP: a client
  that did not reach the page over TLS keeps a secure cookie only when the
  origin is loopback, so a developer whose browser is on another machine
  (issue 044) could not log in at all, and one browser test fails even on
  ``127.0.0.1``;
* every response carries ``X-Frame-Options``, except the two public reports
  that are embedded in another site on purpose.

``common_settings`` is imported directly wherever the production value is what
is being asserted. ``django.conf.settings`` here is ``test_settings``, which
turns the two ``_SECURE`` flags back off, so asserting through it would assert
the override instead of the thing the override exists to relax.
"""

from __future__ import unicode_literals

import imp
import os

import pytest
from django.conf import global_settings, settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from kasvimuseo.tests.conftest import log_in_as_staff
from kasvimuseo.tests.factories import create_planted
from ylaneenkasvit import common_settings

PASSWORD = 'salasana'


@pytest.fixture
def user(db):
    from django.contrib.auth.models import User
    return User.objects.create_user('puutarhuri', 'p@invalid', PASSWORD)


def development_settings():
    """Run ``local_settings.development.py``'s ``modify()`` over a dictionary.

    The file cannot be imported by name -- there is a dot in it, because
    ``dev/kasvimuseo`` copies it to ``local_settings.py`` -- so it is loaded by
    path, the way a settings module never is and a test has to be.
    """
    path = os.path.join(os.path.dirname(common_settings.__file__),
                        'local_settings.development.py')
    module = imp.load_source(str('local_settings_development'), path)
    values = {'INSTALLED_APPS': (),
              'DATABASES': {'default': {}}}
    module.modify(values)
    return values


# What production gets.

def test_the_session_cookie_is_secure_in_the_settings_production_loads():
    assert common_settings.SESSION_COOKIE_SECURE is True


def test_the_csrf_cookie_is_secure_in_the_settings_production_loads():
    assert common_settings.CSRF_COOKIE_SECURE is True


def test_a_login_issues_a_secure_session_cookie(client, user):
    """The regression test for the session half.

    Django 1.5 defaults ``SESSION_COOKIE_SECURE`` to ``False``, so without the
    setting this is a cookie with no ``Secure`` attribute and a browser sends it
    to ``http://kasvit.ambitone.com/`` in cleartext. The production value is
    read from ``common_settings`` rather than written out again, so this fails
    if that value is removed or turned off.
    """
    with override_settings(
            SESSION_COOKIE_SECURE=common_settings.SESSION_COOKIE_SECURE):
        response = client.post(reverse('login'),
                               {'username': user.username,
                                'password': PASSWORD})

    assert response.status_code == 302, 'the login did not succeed'
    assert response.cookies['sessionid']['secure']


def test_a_page_with_a_form_issues_a_secure_csrf_cookie(client, db):
    """The CSRF half, on a GET: the cookie is only set once a template has
    rendered the token, which a login redirect never does."""
    with override_settings(
            CSRF_COOKIE_SECURE=common_settings.CSRF_COOKIE_SECURE):
        response = client.get(reverse('login'))

    assert response.status_code == 200
    assert response.cookies['csrftoken']['secure']


# What development and the suite get, which is the opposite, on purpose.

def test_the_suite_serves_plain_http():
    """The browser tests run these settings from gunicorn on ``http://`` and log
    into the admin. With the production value in place one of them fails --
    measured, and named in ``test_settings.py`` -- on a request Playwright
    makes outside the page, which carries no secure cookie."""
    assert settings.SESSION_COOKIE_SECURE is False
    assert settings.CSRF_COOKIE_SECURE is False


def test_the_development_server_serves_plain_http():
    values = development_settings()
    assert values['SESSION_COOKIE_SECURE'] is False
    assert values['CSRF_COOKIE_SECURE'] is False


# Framing.

def test_the_clickjacking_middleware_is_installed():
    assert ('django.middleware.clickjacking.XFrameOptionsMiddleware'
            in common_settings.MIDDLEWARE_CLASSES)


def test_the_frame_options_value_is_written_out_rather_than_inherited():
    """``SAMEORIGIN`` is Django 1.5's default too, so this pins the decision
    rather than a behaviour: Django 3.0 changes that default to ``DENY``, and
    the upgrade should not deliver that as a surprise."""
    assert common_settings.X_FRAME_OPTIONS == 'SAMEORIGIN'


def test_an_ordinary_page_refuses_to_be_framed(client, db):
    response = client.get(reverse('login'))
    assert response['X-Frame-Options'] == 'SAMEORIGIN'


def test_the_admin_refuses_to_be_framed(admin_client):
    response = admin_client.get(reverse('admin:index'))
    assert response['X-Frame-Options'] == 'SAMEORIGIN'


def test_the_label_editor_refuses_to_be_framed(client, db):
    log_in_as_staff(client)
    response = client.get(reverse('planting-label'))
    assert response['X-Frame-Options'] == 'SAMEORIGIN'


@pytest.mark.parametrize('name, kwargs', [
    ('planted-species-list', {}),
    ('planted-species-compact', {'species_external_ids': '1'}),
])
def test_the_embedded_reports_are_exempt(client, db, name, kwargs):
    """The two pages ``planted-species-iframe.js`` embeds in the museum's other
    site. ``SAMEORIGIN`` would leave that frame blank, so they carry no header
    at all -- and if the exemption is ever dropped, this says so before the
    embed does.

    The compact report is a 404 with nothing planted, and a 404 is rendered by
    the handler rather than by the exempted view, so there has to be something
    for it to show.
    """
    create_planted(name_fi='ahdekaunokki', external_id=1)

    response = client.get(reverse(name, kwargs=kwargs))

    assert response.status_code == 200
    assert 'X-Frame-Options' not in response


def test_csrf_cookie_httponly_is_not_a_setting_this_django_has():
    """Why ``CSRF_COOKIE_HTTPONLY`` is left unset (issue 059).

    Django 1.5 has no such setting: ``CsrfViewMiddleware`` passes no
    ``httponly`` to ``set_cookie``, so writing it in ``common_settings`` would
    be a setting Django ignores -- issue 019's mistake, in a different field.
    This is expected to fail deliberately when the upgrade reaches Django 1.6,
    which adds it: the answer then is still not to turn it on until the label
    editor stops reading the token out of ``document.cookie``.
    """
    assert not hasattr(global_settings, 'CSRF_COOKIE_HTTPONLY')
    assert not hasattr(common_settings, 'CSRF_COOKIE_HTTPONLY')
