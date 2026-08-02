# -*- coding: utf-8 -*-
"""Tests for the project-level entry points in ``ylaneenkasvit``.

The URLconf's redirect, the jqm login/logout views and the Grappelli index
dashboard are what a user meets before any ``kasvimuseo`` view runs, so they
are exercised through the test client rather than by calling the callables.
"""

from __future__ import unicode_literals

import io
import os

import pytest
from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission, User
from django.contrib.staticfiles import finders
from django.core.urlresolvers import resolve, reverse
from django.test.utils import override_settings
from django.utils.translation import ugettext

from kasvimuseo.tests.conftest import jpeg_bytes
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


def module_title(title, collapsible=False):
    return '<h2 class="module_title{0}">{1}</h2>'.format(
        ' grp-collapse-handler' if collapsible else '', ugettext(title))


# The reports and tools the "Reports and tools" module links to. Every custom
# view outside the admin is reachable from here: the two which need object ids
# in the URL are reached through the pages these links lead to -- the species
# sheets through the ``Species`` changelist action, the bed maps through the
# module below.
DASHBOARD_LINKS = ['planted-species-list',
                   'admin:kasvimuseo_species_changelist',
                   'admin:kasvimuseo_observation_changelist',
                   'planting-label',
                   'pl-gallery-archive']


@pytest.mark.parametrize('url_name', DASHBOARD_LINKS)
def test_dashboard_links_to_every_report(admin_client, url_name):
    response = admin_client.get(reverse('admin:index'))

    assert 'href="{0}"'.format(reverse(url_name)) in content(response)


@pytest.fixture
def staff_client(client, db):
    """Logged in as a gardener, not an administrator.

    The museum's own ``käyttäjä`` group grants add/change/delete on the
    ``kasvimuseo`` and ``photologue`` models and nothing from ``auth``, which
    is what the three non-superuser accounts in production have.
    """
    user = User.objects.create_user('puutarhuri', 'p@invalid', PASSWORD)
    user.is_staff = True
    user.save()
    user.user_permissions = Permission.objects.filter(
        content_type__app_label__in=('kasvimuseo', 'photologue'))
    client.login(username=user.username, password=PASSWORD)
    return client


def test_dashboard_serves_a_staff_member_without_admin_rights(staff_client):
    """The reports are for the gardeners, so they must not need admin rights.

    The link lists carry no permission check of their own -- every report they
    point at is either a public view or a changelist the group can open.
    """
    body = content(staff_client.get(reverse('admin:index')))

    assert module_title('Reports and tools') in body
    for url_name in DASHBOARD_LINKS:
        assert 'href="{0}"'.format(reverse(url_name)) in body
    # Grappelli filters ModelList modules by permission, so the group that
    # lists Users and Groups disappears for a user with no ``auth`` rights.
    assert module_title('Administration') not in body
    assert 'href="{0}"'.format(reverse('admin:auth_user_changelist')) not in body


def test_dashboard_describes_the_reports(admin_client):
    """The overridden link list template renders ``description`` as help text."""
    body = content(admin_client.get(reverse('admin:index')))

    assert ('<p class="grp-help">{0}</p>'
            .format(ugettext('The public Photologue galleries'))) in body


def test_dashboard_links_to_the_map_of_every_bed(admin_client, db):
    beds = [Bed.objects.create(name='1', plot=Plot.objects.create(name='Piha')),
            Bed.objects.create(name='Kellarinseinusta')]

    body = content(admin_client.get(reverse('admin:index')))

    assert module_title('Bed maps', collapsible=True) in body
    for bed in beds:
        assert '<a class="grp-link-internal" href="{0}">{1}</a>'.format(
            reverse('bed-map', kwargs={'pk': bed.pk}), bed) in body


def test_dashboard_skips_the_bed_maps_without_beds(admin_client):
    """``DashboardModule.is_empty`` drops a link list with no children."""
    body = content(admin_client.get(reverse('admin:index')))

    assert module_title('Bed maps', collapsible=True) not in body


MODEL_GROUP_TITLES = ['Base data', 'Observations and plantings', 'Photos']


@pytest.mark.parametrize('title', MODEL_GROUP_TITLES)
def test_dashboard_names_every_model_group(admin_client, title):
    """The generated groups had no titles, so the page opened unlabelled."""
    response = admin_client.get(reverse('admin:index'))

    assert module_title(title, collapsible=True) in content(response)


@pytest.mark.parametrize('title', MODEL_GROUP_TITLES)
def test_dashboard_leaves_the_model_groups_open(admin_client, title):
    """Naming the groups made them collapsible, so pin that they start open.

    Grappelli 2.4 reads the initial state from the ``grp-open``/``grp-closed``
    class ``render_css_classes`` adds to the module's ``div``; nothing on the
    dashboard should hide its model links behind a click.
    """
    body = content(admin_client.get(reverse('admin:index')))

    before = body[:body.index(module_title(title, collapsible=True))]
    opening_tag = '<div' + before.rsplit('<div', 1)[-1]
    assert 'grp-open' in opening_tag
    assert 'grp-closed' not in opening_tag


def test_dashboard_renders_the_reports_module(admin_client):
    response = admin_client.get(reverse('admin:index'))

    assert module_title('Reports and tools') in content(response)


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


def test_photologue_gallery_index_renders_on_an_empty_database(client, db):
    """Photologue's own gallery index is a date archive with ``allow_empty`` off.

    Photologue's own route raises ``Http404`` while no gallery exists, so the
    link the admin dashboard carries answered 404 on the database
    ``dev/kasvimuseo db bootstrap`` builds. ``ylaneenkasvit.urls`` declares the
    same path and the same URL name ahead of the include with
    ``allow_empty=True``, so it renders an empty list instead.
    """
    with override_settings(DEBUG=False):
        response = client.get(reverse('pl-gallery-archive'))

    assert reverse('pl-gallery-archive') == '/photologue/gallery/'
    assert response.status_code == 200
    assert list(response.context['latest']) == []


def test_photologue_gallery_index_lists_a_gallery(client, db):
    """The override changes nothing but the empty case."""
    gallery = Gallery.objects.create(title='Kesä 2012', slug='kesa-2012')

    response = client.get(reverse('pl-gallery-archive'))

    assert response.status_code == 200
    assert list(response.context['latest']) == [gallery]
    assert gallery.title in content(response)


def test_grappelli_urls_are_wired(admin_client):
    plot = add_plot_through_the_admin(admin_client)
    url = reverse('grp_related_lookup')

    response = admin_client.get(url, {'app_label': 'kasvimuseo',
                                      'model_name': 'plot',
                                      'object_id': plot.pk})

    assert url.startswith('/grappelli/')
    assert response.status_code == 200
    assert plot.name in content(response)


# Issue 022: the dead ``/media/grappelli/`` route is gone, and with it
# ``ADMIN_MEDIA_PREFIX``. These pin what serves the admin's chrome instead.

def test_the_admin_gets_its_grappelli_assets_from_staticfiles(admin_client):
    """The stylesheet is named under ``STATIC_URL`` and found in the package.

    grappelli 2.4.5 keeps its assets in ``static/``; the deleted route pointed
    at a ``media/`` directory the package does not have. Nothing consults
    ``ADMIN_MEDIA_PREFIX`` either -- grappelli's own ``admin/base.html`` fills
    ``window.__admin_media_prefix__`` from ``{% static "grappelli/" %}``.
    """
    stylesheet = 'grappelli/stylesheets/screen.css'

    response = admin_client.get(reverse('admin:index'))

    assert settings.STATIC_URL + stylesheet in content(response)
    assert finders.find(stylesheet) is not None


def test_media_under_grappelli_reaches_the_media_view(client, db, media_root):
    """The deleted route matched this prefix ahead of the ``media`` one.

    It served a directory that does not exist, so it 404ed everything; the
    ordering is the only thing it ever decided (issue 048). With it gone the
    prefix is ordinary media, served from ``MEDIA_ROOT`` like any other path.
    """
    os.mkdir(os.path.join(media_root, 'grappelli'))
    with io.open(os.path.join(media_root, 'grappelli', 'kukka.jpg'),
                 'wb') as image_file:
        image_file.write(jpeg_bytes())

    response = client.get('/media/grappelli/kukka.jpg')

    assert resolve('/media/grappelli/kukka.jpg').url_name == 'media'
    assert response.status_code == 200
    assert b''.join(response.streaming_content) == jpeg_bytes()


def test_unknown_url_returns_404(client, db):
    with override_settings(DEBUG=False):
        response = client.get('/ei-ole-olemassa/')

    assert response.status_code == 404
    assert '404 - Page not found' in content(response)


# Issue 048: the development server serves its own uploaded media and asks the
# production media host for what it does not have. The route only exists when
# ``MEDIA_URL`` is a local path, which ``test_settings`` makes it, so these run
# against the same wiring the development settings get.

def test_media_serves_a_local_file(client, db, media_root):
    with io.open(os.path.join(media_root, 'kukka.jpg'), 'wb') as image_file:
        image_file.write(jpeg_bytes())

    response = client.get('/media/kukka.jpg')

    assert response.status_code == 200
    assert response['Content-Type'] == 'image/jpeg'
    assert b''.join(response.streaming_content) == jpeg_bytes()


def test_media_serves_a_photologue_upload(client, db, photo_factory):
    """The path a rendered page actually asks for, end to end."""
    photo = photo_factory()

    response = client.get(photo.image.url)

    assert photo.image.url.startswith('/media/photologue/photos/')
    assert response.status_code == 200


@pytest.mark.parametrize('path, expected', [
    ('photologue/photos/IMG_2272_linkedin.jpeg',
     'https://media.example.com/photologue/photos/IMG_2272_linkedin.jpeg'),
    # Photologue keeps the uploaded file name, spaces, umlauts and all.
    ('photologue/photos/kevät kukassa.jpg',
     'https://media.example.com/photologue/photos/'
     'kev%C3%A4t%20kukassa.jpg'),
])
def test_media_redirects_a_missing_file_to_the_fallback_host(
        client, db, media_root, path, expected):
    with override_settings(MEDIA_FALLBACK_URL='https://media.example.com/'):
        response = client.get('/media/' + path)

    assert response.status_code == 302
    assert response['Location'] == expected


def test_media_404s_a_missing_file_without_a_fallback(client, db, media_root):
    """``MEDIA_FALLBACK_URL`` is empty everywhere but the development settings."""
    with override_settings(DEBUG=False, MEDIA_FALLBACK_URL=''):
        response = client.get('/media/photologue/photos/ei-ole.jpeg')

    assert response.status_code == 404


def test_media_does_not_serve_outside_media_root(client, db, media_root):
    """``django.views.static.serve`` strips ``..`` before it reaches the disk.

    Without a fallback the escape attempt is a 404; with one it is a redirect
    to the fallback host, which is the same public host the URL would have
    named anyway. Either way nothing outside ``MEDIA_ROOT`` is served.
    """
    with override_settings(DEBUG=False, MEDIA_FALLBACK_URL=''):
        response = client.get('/media/../ylaneenkasvit/local_settings.py')

    assert response.status_code in (301, 302, 404)
    assert not response.get('Content-Type', '').startswith('text/x-python')
