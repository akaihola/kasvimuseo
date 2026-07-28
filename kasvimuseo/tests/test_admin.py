# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.admin``.

The display callables are called straight on a ``ModelAdmin`` instance; the
smoke tests go through ``admin_client`` because the changelist and add pages
are what catch form- and template-construction breakage.
"""

from __future__ import unicode_literals

import pytest
from django.contrib import admin as django_admin
from django.core.urlresolvers import NoReverseMatch, reverse

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


@pytest.mark.django_db
def test_planted_species_report():
    factories.create_species(name_fi='valkonarsissi', external_id=11)
    factories.create_species(name_fi='keltanarsissi', external_id=22)

    response = admin.planted_species_report(
        None, None, Species.objects.order_by('external_id'))

    assert response.status_code == 302
    assert response['Location'] == reverse(
        'planted-species', kwargs={'species_external_ids': '11,22'})


@pytest.mark.django_db
def test_planted_species_report_with_null_external_id():
    """A species without an id makes the action raise instead of redirect.

    ``external_id`` is nullable, ``unicode(None)`` is ``'None'``, and the
    ``planted-species`` URL only accepts ``[\\d,]+``.

    See docs/issues/009.
    """
    factories.create_species(external_id=None)

    with pytest.raises(NoReverseMatch):
        admin.planted_species_report(None, None, Species.objects.all())


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
