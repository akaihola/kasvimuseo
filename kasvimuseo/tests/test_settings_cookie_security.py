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

import os

import pytest
from django.conf import global_settings, settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from kasvimuseo.tests.conftest import log_in_as_staff
from kasvimuseo.tests.factories import create_planted
from ylaneenkasvit import common_settings

PASSWORD = 'salasana'
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(common_settings.__file__)))


@pytest.fixture
def user(db):
    from django.contrib.auth.models import User
    return User.objects.create_user('puutarhuri', 'p@invalid', PASSWORD)


def development_settings():
    """Import ``ylaneenkasvit.development_settings`` and hand back the module.

    It is a settings module like any other since issue 067, so it is imported
    rather than loaded by path -- which is what its predecessor,
    ``local_settings.development.py``, had to be: a template with a dot in its
    name, holding a ``modify()`` function run over a dictionary. Being a module
    is the fix, so this is also the assertion that it is one.
    """
    from ylaneenkasvit import development_settings
    return development_settings


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
    settings_module = development_settings()
    assert settings_module.SESSION_COOKIE_SECURE is False
    assert settings_module.CSRF_COOKIE_SECURE is False


def test_the_development_relaxation_is_in_a_tracked_file():
    """Issue 067, and the whole of what it changed.

    The two lines above were right before 067 as well, and the development
    server still served ``Secure`` cookies over plain HTTP, because they were in
    ``local_settings.development.py`` -- a template copied to the untracked
    ``local_settings.py`` when a checkout has none and never again, so a
    checkout older than issue 059 never received them. Asserting the values is
    therefore not enough: what a browser gets depends on the file being one
    ``git pull`` delivers.
    """
    path = development_settings().__file__
    assert os.path.basename(path).startswith('development_settings')

    with open(os.path.join(REPO_ROOT, '.gitignore')) as ignores:
        ignored = ignores.read()

    # The one settings file that is still untracked, and the line that says so:
    # if this ever stops matching, read the rest of this assertion again.
    assert '/ylaneenkasvit/local_settings.py' in ignored
    assert 'development_settings' not in ignored, (
        'the development settings are excluded from the repository, which is'
        ' the shape of issue 067')


def test_the_superseded_template_is_gone():
    """Nothing copies a settings file into place any more, so a leftover
    template would be a second, stale statement of the same settings -- and the
    copies it already made are what 067 is about."""
    assert not os.path.exists(os.path.join(
        REPO_ROOT, 'ylaneenkasvit', 'local_settings.development.py'))


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


def test_csrf_cookie_httponly_is_a_live_setting_now_and_stays_off():
    """Why ``CSRF_COOKIE_HTTPONLY`` is still left unset (issue 059).

    Its predecessor asserted that Django had no such setting, which was true of
    1.5 and is the reason 059 declined to write one Django would ignore. It
    said in as many words that it would fail on the day the upgrade reached
    Django 1.6, and it did -- upgrade plan Stage 3, the first thing that stage's
    suite run found. So the assertion moves to the other half of 059's ruling,
    which the arriving setting turns from a nicety into a live decision: the
    default is ``False``, the label editor's save still reads the token out of
    ``document.cookie``, and turning it on would give every gardener the "this
    browser has no csrftoken cookie" alert instead of a working Save. Reading
    the ``{% csrf_token %}`` input that page already renders is the prerequisite
    and is a change to the editor, not to the settings.
    """
    assert global_settings.CSRF_COOKIE_HTTPONLY is False
    assert not hasattr(common_settings, 'CSRF_COOKIE_HTTPONLY')


def test_the_csrf_cookie_is_readable_by_the_label_editors_javascript(client,
                                                                    db):
    """The behavioural half of the assertion above, which the settings cannot
    make on their own: Django 1.6's ``CsrfViewMiddleware`` now passes
    ``httponly`` to ``set_cookie``, so what is being pinned is that the cookie
    it issues is still one ``document.cookie`` can see."""
    log_in_as_staff(client)

    response = client.get(reverse('planting-label'))

    assert response.status_code == 200
    assert response.cookies['csrftoken']['httponly'] == ''
