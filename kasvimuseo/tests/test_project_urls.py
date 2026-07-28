# -*- coding: utf-8 -*-
"""Tests for the project-level entry points in ``ylaneenkasvit``.

The URLconf's redirect, the jqm login/logout views and the Grappelli index
dashboard are what a user meets before any ``kasvimuseo`` view runs, so they
are exercised through the test client rather than by calling the callables.
"""

from __future__ import unicode_literals

import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.translation import ugettext

from kasvimuseo.models import Bed, Care, Contact, Location, Observation
from kasvimuseo.models import Planting, Plot, Species
from photologue.models import Gallery, Photo

PASSWORD = 'salasana'


@pytest.fixture
def user(db):
    return User.objects.create_user('puutarhuri', 'p@invalid', PASSWORD)


def content(response):
    """``response.content`` is bytes on Python 2.7; compare text with text."""
    return response.content.decode('utf-8')


@pytest.mark.parametrize('logged_in', [False, True])
def test_root_redirects_to_admin(client, user, logged_in):
    if logged_in:
        client.login(username=user.username, password=PASSWORD)

    response = client.get('/')

    assert response.status_code == 302
    assert response['Location'].endswith('/admin/')


def test_login_page_shows_the_credential_fields(client, db):
    response = client.get(reverse('login'))

    assert response.status_code == 200
    body = content(response)
    assert 'name="username"' in body
    assert 'name="password"' in body


def test_login_with_valid_credentials(client, user):
    response = client.post(reverse('login'),
                           {'username': user.username, 'password': PASSWORD})

    assert response.status_code == 302
    assert client.session['_auth_user_id'] == user.pk


def test_login_with_invalid_credentials(client, user):
    response = client.post(reverse('login'),
                           {'username': user.username, 'password': 'väärin'})

    assert response.status_code == 200
    assert 'errorlist' in content(response)
    assert '_auth_user_id' not in client.session


def test_logout_ends_the_session(client, user):
    client.login(username=user.username, password=PASSWORD)
    assert '_auth_user_id' in client.session

    response = client.get(reverse('logout'))

    assert response.status_code == 200
    assert 'Your account has been logged out.' in content(response)
    assert '_auth_user_id' not in client.session


@pytest.mark.django_db
def test_admin_page_gates_anonymous_users_with_the_login_form(client):
    """Django 1.5's admin answers with the login form in place of the page.

    It renders it under the requested URL rather than redirecting to
    ``admin:login``, so what this pins is the 200 with the login form and no
    data in it.
    """
    species = Species.objects.create(name_fi='valkonarsissi', type=2)

    response = client.get(reverse('admin:kasvimuseo_species_changelist'))
    body = content(response)

    assert response.status_code == 200
    assert 'name="username"' in body
    assert 'name="password"' in body
    assert species.name_fi not in body


# The models each of the dashboard's ModelList modules is configured with; a
# changelist link for every one of them proves ``init_with_context`` ran, since
# Grappelli's dashboard index template renders nothing but the dashboard.
DASHBOARD_MODELS = [Species, Location, Contact, Plot, Bed,  # first module
                    Observation, Planting, Care,            # second module
                    Gallery, Photo,                         # photologue module
                    User]                                   # "Administration"


@pytest.mark.parametrize('model', DASHBOARD_MODELS,
                         ids=[model.__name__ for model in DASHBOARD_MODELS])
def test_dashboard_links_to_every_configured_model(admin_client, model):
    response = admin_client.get(reverse('admin:index'))

    assert response.status_code == 200
    url = reverse('admin:{0}_{1}_changelist'.format(model._meta.app_label,
                                                    model._meta.module_name))
    assert 'href="{0}"'.format(url) in content(response)


def module_title(title):
    return '<h2 class="module_title">{0}</h2>'.format(ugettext(title))


def test_dashboard_renders_the_administration_module(admin_client):
    """The only module of the five with a title and no log entries needed."""
    response = admin_client.get(reverse('admin:index'))

    assert module_title('Administration') in content(response)


def add_plot_through_the_admin(admin_client, name='Piha'):
    """Add a ``Plot``, inline management form and all, so a LogEntry is written."""
    response = admin_client.post(reverse('admin:kasvimuseo_plot_add'),
                                 {'name': name,
                                  'bed_set-TOTAL_FORMS': '0',
                                  'bed_set-INITIAL_FORMS': '0',
                                  'bed_set-MAX_NUM_FORMS': ''})
    assert response.status_code == 302, 'the add form did not validate'
    return Plot.objects.get(name=name)


def test_dashboard_recent_actions_lists_an_admin_addition(admin_client):
    plot = add_plot_through_the_admin(admin_client)
    entry = LogEntry.objects.get()

    body = content(admin_client.get(reverse('admin:index')))

    # The module is skipped entirely while it is empty (``DashboardModule
    # .is_empty``), so its title only appears once there is an entry to list.
    assert module_title('Recent Actions') in body
    assert entry.object_repr == plot.name
    assert '<a href="{0}">{1}</a>'.format(entry.get_admin_url(),
                                          plot.name) in body


def test_photologue_urls_are_wired(client, db):
    response = client.get('/photologue/')

    assert response.status_code == 301  # photologue's root is a RedirectView
    assert response['Location'].endswith(reverse('pl-gallery-archive'))
    assert reverse('pl-gallery-archive').startswith('/photologue/')


def test_grappelli_urls_are_wired(admin_client):
    plot = add_plot_through_the_admin(admin_client)
    url = reverse('grp_related_lookup')

    response = admin_client.get(url, {'app_label': 'kasvimuseo',
                                      'model_name': 'plot',
                                      'object_id': plot.pk})

    assert url.startswith('/grappelli/')
    assert response.status_code == 200
    assert plot.name in content(response)


def test_unknown_url_returns_404(client, db):
    with override_settings(DEBUG=False):
        response = client.get('/ei-ole-olemassa/')

    assert response.status_code == 404
    assert '404 - Page not found' in content(response)
