# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.admin``.

The display callables are called straight on a ``ModelAdmin`` instance; the
smoke tests go through ``admin_client`` because the changelist and add pages
are what catch form- and template-construction breakage.
"""

from __future__ import unicode_literals

import pytest
from django.contrib import admin as django_admin
from django.contrib.messages.storage import default_storage
from django.core.urlresolvers import reverse

from kasvimuseo import admin
from kasvimuseo.models import (
    Bed, Care, Contact, Location, Observation, Planting, Plot, Species)
from kasvimuseo.tests import factories
from photologue.models import Photo


@pytest.mark.django_db
def test_planting_admin_coordinates():
    """Both pairs are shown -- offsets first, then the size."""
    planting = factories.create_planting(distance_left=10, distance_front=20,
                                         width=30, depth=40)
    modeladmin = admin.PlantingAdmin(Planting, django_admin.site)

    assert modeladmin.coordinates(planting) == '(10cm,20cm)<br>30×40cm'


@pytest.mark.django_db
def test_bed_admin_map():
    bed = factories.create_bed()
    modeladmin = admin.BedAdmin(Bed, django_admin.site)

    result = modeladmin.map(bed)

    url = reverse('bed-map', kwargs={'pk': bed.pk})
    assert result.startswith('<a href="{0}">'.format(url))
    assert result.endswith('</a>')


@pytest.mark.django_db
def test_observation_admin_page():
    observation = factories.create_observation(external_id=42)
    modeladmin = admin.ObservationAdmin(Observation, django_admin.site)

    result = modeladmin.page(observation)

    url = reverse('planted-observation', args=[observation.external_id])
    assert result == '<a href="{0}">sivu</a>'.format(url)


@pytest.mark.django_db
def test_observation_admin_page_without_an_external_id():
    """``external_id`` is optional, and the public URL is keyed by it."""
    observation = factories.create_observation()
    modeladmin = admin.ObservationAdmin(Observation, django_admin.site)

    assert observation.external_id is None
    assert modeladmin.page(observation) == ''


@pytest.mark.django_db
def test_photo_admin_image_filename(photo_factory):
    photo = photo_factory()
    modeladmin = admin.PhotoAdmin(Photo, django_admin.site)

    result = modeladmin.image_filename(photo)

    assert '/' in photo.image.name  # photologue stores photos in a subdirectory
    assert result == photo.image.name.split('/')[-1]


@pytest.mark.django_db
def test_species_admin_photo_image(photo_factory):
    species = factories.create_species(photo=photo_factory())
    modeladmin = admin.SpeciesAdmin(Species, django_admin.site)

    result = modeladmin.photo_image(species)

    assert '/' not in result
    assert result.startswith('valkonarsissi-kukassa')
    assert result.endswith('.jpg')


@pytest.mark.django_db
def test_species_admin_photo_image_without_photo():
    species = factories.create_species()
    modeladmin = admin.SpeciesAdmin(Species, django_admin.site)

    assert modeladmin.photo_image(species) == ''


@pytest.fixture
def species_admin_action(rf):
    """Call ``planted_species_report`` the way the admin does.

    Returns a callable taking a queryset and giving back the action's response
    and the messages it left. ``message_user`` goes through
    ``django.contrib.messages``, whose storage is normally installed by
    ``MessageMiddleware``; ``RequestFactory`` runs no middleware, so install it
    here.
    """
    modeladmin = admin.SpeciesAdmin(Species, django_admin.site)
    request = rf.post(reverse('admin:kasvimuseo_species_changelist'))
    request.session = {}
    request._messages = default_storage(request)

    def call(queryset):
        response = admin.planted_species_report(modeladmin, request, queryset)
        return response, [message.message for message in request._messages]

    return call


@pytest.mark.django_db
def test_planted_species_report(species_admin_action):
    factories.create_species(name_fi='valkonarsissi', external_id=11)
    factories.create_species(name_fi='keltanarsissi', external_id=22)

    response, messages = species_admin_action(
        Species.objects.order_by('external_id'))

    assert response.status_code == 302
    assert response['Location'] == reverse(
        'planted-species', kwargs={'species_external_ids': '11,22'})
    assert messages == []


@pytest.mark.django_db
def test_planted_species_report_with_null_external_id(species_admin_action):
    """A species without an id is left out, and the user is told which.

    ``external_id`` is nullable and the ``planted-species`` URL only accepts
    ``[\\d,]+``, so such a species cannot appear in the report at all.

    See docs/issues/009.
    """
    factories.create_species(name_fi='valkonarsissi', external_id=11)
    factories.create_species(name_fi='nimetön', external_id=None)

    response, messages = species_admin_action(
        Species.objects.order_by('external_id'))

    assert response.status_code == 302
    assert response['Location'] == reverse(
        'planted-species', kwargs={'species_external_ids': '11'})
    assert messages == ['Raportista jäivät pois, koska niillä ei ole '
                        'LajiNroa: nimetön']


@pytest.mark.django_db
def test_planted_species_report_with_only_null_external_ids(
        species_admin_action):
    """With nothing left to report on, say so rather than redirect."""
    factories.create_species(name_fi='nimetön', external_id=None)

    response, messages = species_admin_action(Species.objects.all())

    assert response is None
    assert messages == ['Raportista jäivät pois, koska niillä ei ole '
                        'LajiNroa: nimetön',
                        'Yhdelläkään valitulla lajilla ei ole LajiNroa, '
                        'joten raporttia ei voi luoda.']


@pytest.mark.django_db
def test_planted_species_report_through_the_admin(admin_client):
    """The action really is reachable, and ``message_user`` really works.

    Issue 023 notes that ``django.contrib.messages`` is not in
    ``INSTALLED_APPS``; its middleware nevertheless is, by way of Django's
    default ``MIDDLEWARE_CLASSES``, which is what ``message_user`` needs.
    """
    factories.create_species(name_fi='valkonarsissi', external_id=11)
    factories.create_species(name_fi='nimetön', external_id=None)
    url = reverse('admin:kasvimuseo_species_changelist')
    selected = [species.pk for species in Species.objects.all()]

    response = admin_client.post(url, {'action': 'planted_species_report',
                                       '_selected_action': selected})

    assert response.status_code == 302
    assert response['Location'].endswith(
        reverse('planted-species', kwargs={'species_external_ids': '11'}))
    # The message survives the redirect, so it is on the next page the
    # gardener sees rather than lost.
    changelist = admin_client.get(url)
    assert ('Raportista jäivät pois, koska niillä ei ole LajiNroa: nimetön'
            in changelist.content.decode('utf-8'))


REGISTERED_MODELS = [Species, Location, Planting, Observation, Care, Contact,
                     Plot, Bed, Photo]


@pytest.fixture
def sample_data(db, photo_factory):
    """One row of every registered model, so the changelists render rows."""
    planting = factories.create_planted(
        bed=factories.create_bed(plot=factories.create_plot()))
    factories.create_care(planting)
    Contact.objects.create(last_name='Kaihola', first_name='Antti')
    species = planting.observation.species
    species.photo = photo_factory()
    species.save()


@pytest.mark.parametrize('page', ['changelist', 'add'])
@pytest.mark.parametrize('model', REGISTERED_MODELS,
                         ids=[model.__name__ for model in REGISTERED_MODELS])
def test_admin_page_returns_200(admin_client, sample_data, model, page):
    assert model in django_admin.site._registry
    url = reverse('admin:{0}_{1}_{2}'.format(model._meta.app_label,
                                             model._meta.module_name,
                                             page))

    assert admin_client.get(url).status_code == 200
