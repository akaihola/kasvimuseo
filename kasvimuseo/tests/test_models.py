# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.models``, above all the public-visibility rules."""

from __future__ import unicode_literals

import datetime

import pytest
from django.utils.encoding import force_text
from django.utils.translation import override

from kasvimuseo import models
from kasvimuseo.tests.factories import (create_care, create_location,
                                        create_observation, create_planted,
                                        create_planting, create_species)


DATE = datetime.date(2020, 6, 1)


# --------------------------------------------------------------------------
# public_planted() -- the visibility matrix
# --------------------------------------------------------------------------

@pytest.mark.django_db
def test_public_planted_private_bed_is_hidden():
    planting = create_planted(public=False)
    assert list(models.Planting.objects.public_planted()) == []
    assert list(models.Observation.objects.public_planted()) == []
    assert list(models.Species.objects.public_planted()) == []
    assert planting.is_public_planted() is False


@pytest.mark.django_db
def test_public_planted_no_cares_is_visible():
    planting = create_planted()
    assert list(models.Planting.objects.public_planted()) == [planting]
    assert list(models.Observation.objects.public_planted()) == [
        planting.observation]
    assert list(models.Species.objects.public_planted()) == [
        planting.observation.species]
    assert planting.is_public_planted() is True


@pytest.mark.django_db
def test_public_planted_removed_is_hidden():
    planting = create_planted(removed=True)
    assert list(models.Planting.objects.public_planted()) == []
    assert list(models.Observation.objects.public_planted()) == []
    assert planting.is_public_planted() is False


@pytest.mark.django_db
def test_public_planted_last_care_zero_is_hidden():
    planting = create_planted(cares=[5, 0])
    assert list(models.Planting.objects.public_planted()) == []
    assert list(models.Observation.objects.public_planted()) == []
    assert list(models.Species.objects.public_planted()) == []
    assert planting.is_public_planted() is False


@pytest.mark.django_db
def test_public_planted_last_care_positive_is_visible():
    planting = create_planted(cares=[0, 4])
    assert list(models.Planting.objects.public_planted()) == [planting]
    assert list(models.Observation.objects.public_planted()) == [
        planting.observation]
    assert list(models.Species.objects.public_planted()) == [
        planting.observation.species]
    assert planting.is_public_planted() is True


@pytest.mark.django_db
def test_public_planted_uses_date_order_not_pk_order():
    """The newest care by *date* decides, even when it was entered first."""
    planting = create_planting()
    newest = create_care(planting, count=7, date=DATE + datetime.timedelta(30))
    oldest = create_care(planting, count=0, date=DATE)
    assert oldest.pk > newest.pk
    assert planting.last_care == newest
    assert planting.is_public_planted() is True
    assert list(models.Planting.objects.public_planted()) == [planting]


@pytest.mark.django_db
def test_public_planted_picks_only_the_visible_rows():
    visible = create_planted(name_fi='valkonarsissi')
    create_planted(name_fi='keltanarsissi', cares=[0])
    create_planted(name_fi='sinivuokko', public=False)
    create_planted(name_fi='kielo', removed=True)
    assert list(models.Planting.objects.public_planted()) == [visible]
    # 'kielo' is only there because SpeciesManager ignores removal_date; see
    # test_species_manager_ignores_removal_date.
    assert [s.name_fi for s in models.Species.objects.public_planted()] == [
        'kielo', 'valkonarsissi']


@pytest.mark.django_db
def test_species_visible_when_only_one_of_its_plantings_is():
    species = create_species()
    hidden = create_planted(species=species, cares=[0])
    visible = create_planted(species=species)
    assert hidden.observation.species == visible.observation.species
    assert list(models.Species.objects.public_planted()) == [species]


@pytest.mark.django_db
def test_species_manager_ignores_removal_date():
    """Pins a known inconsistency: ``SpeciesManager`` never looks at
    ``removal_date``, so a removed planting still makes its species public
    while the planting and observation managers hide it.

    See docs/issues/001."""
    planting = create_planted(removed=True, cares=[4])
    assert list(models.Species.objects.public_planted()) == [
        planting.observation.species]
    assert list(models.Planting.objects.public_planted()) == []
    assert list(models.Observation.objects.public_planted()) == []


# --------------------------------------------------------------------------
# last_care and its accessors
# --------------------------------------------------------------------------

@pytest.mark.django_db
def test_last_care_both_code_paths_agree():
    planting = create_planted(cares=[1, 2, 3])
    plain = models.Planting.objects.get(pk=planting.pk)
    assert not hasattr(plain, '_prefetched_objects_cache')
    prefetched = list(
        models.Planting.objects.prefetch_related('care_set')
        .filter(pk=planting.pk))[0]
    assert hasattr(prefetched, '_prefetched_objects_cache')
    assert plain.last_care.pk == prefetched.last_care.pk
    assert plain.last_care.count == 3


@pytest.mark.django_db
def test_last_care_both_code_paths_agree_out_of_date_order():
    planting = create_planting()
    newest = create_care(planting, count=7, date=DATE + datetime.timedelta(30))
    create_care(planting, count=0, date=DATE)
    plain = models.Planting.objects.get(pk=planting.pk)
    prefetched = list(
        models.Planting.objects.prefetch_related('care_set')
        .filter(pk=planting.pk))[0]
    assert plain.last_care.pk == newest.pk
    assert prefetched.last_care.pk == newest.pk


@pytest.mark.django_db
def test_last_care_is_none_without_cares():
    planting = create_planting()
    assert planting.last_care is None
    prefetched = list(
        models.Planting.objects.prefetch_related('care_set')
        .filter(pk=planting.pk))[0]
    assert prefetched.last_care is None


@pytest.mark.django_db
def test_last_care_accessors_fall_back_to_empty_string():
    planting = create_planting()
    assert planting.last_care_date() == ''
    assert planting.last_care_description() == ''
    assert planting.last_care_count() == ''


@pytest.mark.django_db
def test_last_care_accessors_with_a_care():
    planting = create_planting()
    create_care(planting, count=2, date=DATE, description='kastelu')
    assert planting.last_care_date() == DATE
    assert planting.last_care_description() == 'kastelu'
    assert planting.last_care_count() == 2


@pytest.mark.django_db
def test_observation_external_id():
    planting = create_planted(external_id=42)
    assert planting.observation_external_id() == 42


# --------------------------------------------------------------------------
# get_next_observation_extid -- defect 2
# --------------------------------------------------------------------------

@pytest.mark.django_db
def test_next_observation_extid_on_empty_table():
    assert models.Observation.objects.count() == 0
    with override(None):
        assert force_text(models.get_next_observation_extid()) == \
            'Next available ID: 1'


@pytest.mark.django_db
def test_next_observation_extid_with_only_null_external_ids():
    create_observation(external_id=None)
    with override(None):
        assert force_text(models.get_next_observation_extid()) == \
            'Next available ID: 1'


@pytest.mark.django_db
def test_next_observation_extid_ignores_nulls_among_rows():
    create_observation(external_id=None)
    create_observation(external_id=7)
    create_observation(external_id=3)
    with override(None):
        assert force_text(models.get_next_observation_extid()) == \
            'Next available ID: 8'


@pytest.mark.django_db
def test_observation_add_form_help_text_renders_on_empty_database():
    """The lazy help_text is evaluated when the admin form is built."""
    help_text = models.Observation._meta.get_field('external_id').help_text
    with override(None):
        assert force_text(help_text) == 'Next available ID: 1'


# --------------------------------------------------------------------------
# Species helpers
# --------------------------------------------------------------------------

@pytest.mark.django_db
def test_species_nicknames_is_gone():
    """Defect 1: the broken, callerless ``Species.nicknames`` was deleted."""
    assert not hasattr(models.Species, 'nicknames')


def test_species_name_with_subspecies():
    assert models.Species(name_fi='kielo').name_with_subspecies() == 'kielo'
    assert models.Species(name_fi='kielo',
                          subspecies='alpina').name_with_subspecies() == \
        'kielo/alpina'


def test_species_flowering_time():
    assert models.Species(flowering_start=None).flowering_time() == ''
    assert models.Species(flowering_start=5).flowering_time() == 'V'
    assert models.Species(flowering_start=5,
                          flowering_end=12).flowering_time() == 'V–XII'


# --------------------------------------------------------------------------
# __unicode__
# --------------------------------------------------------------------------

def test_species_unicode():
    assert force_text(models.Species(name_fi='kielo')) == 'kielo'


def test_plot_unicode():
    assert force_text(models.Plot(name='Piha')) == 'Piha'


def test_bed_unicode_without_plot():
    assert force_text(models.Bed(name='1')) == '1'


def test_bed_unicode_with_plot():
    assert force_text(models.Bed(plot=models.Plot(name='Piha'),
                                 name='1')) == 'Piha/1'


def test_contact_unicode():
    assert force_text(models.Contact(last_name='Virtanen',
                                     first_name='Maija')) == 'Virtanen, Maija'


def test_location_unicode():
    assert force_text(models.Location(name='Talo')) == 'Talo'


@pytest.mark.django_db
def test_location_contact_unicode():
    location = create_location(name='Talo')
    contact = models.Contact.objects.create(last_name='Virtanen',
                                            first_name='Maija')
    link = models.LocationContact.objects.create(location=location,
                                                 contact=contact)
    assert force_text(link) == 'Talo/Virtanen, Maija'


@pytest.mark.django_db
def test_observation_unicode_without_variation():
    observation = create_observation(species=create_species(name_fi='kielo'),
                                     origin=create_location(name='Talo'))
    assert force_text(observation) == 'kielo (Talo)'


@pytest.mark.django_db
def test_observation_unicode_with_variation():
    observation = create_observation(species=create_species(name_fi='kielo'),
                                     origin=create_location(name='Talo'),
                                     variation='valkoinen')
    assert force_text(observation) == 'kielo/valkoinen (Talo)'


@pytest.mark.django_db
def test_planting_unicode():
    planting = create_planted(name_fi='kielo')
    assert force_text(planting) == force_text(planting.observation)


@pytest.mark.django_db
def test_care_unicode():
    planting = create_planted(name_fi='kielo')
    care = create_care(planting, count=1, date=DATE, description='kastelu')
    assert force_text(care) == '{0}: {1} / kastelu'.format(
        DATE, force_text(planting))


@pytest.mark.django_db
def test_label_unicode_without_photo():
    label = models.Label.objects.create(species=create_species(name_fi='kielo'))
    assert force_text(label) == 'kielo'


@pytest.mark.django_db
def test_label_unicode_hidden_without_photo():
    label = models.Label.objects.create(species=create_species(name_fi='kielo'),
                                        visible=False)
    with override(None):
        assert force_text(label) == 'kielo [hidden]'


@pytest.mark.django_db
def test_label_unicode_with_photo(photo_factory):
    photo = photo_factory(title='kielo kukassa')
    label = models.Label.objects.create(species=create_species(name_fi='kielo'),
                                        photo=photo)
    assert force_text(label) == 'kielo / {0}'.format(photo.image_filename())


@pytest.mark.django_db
def test_label_unicode_with_photo_hidden(photo_factory):
    photo = photo_factory(title='kielo kukassa')
    label = models.Label.objects.create(species=create_species(name_fi='kielo'),
                                        photo=photo, visible=False)
    with override(None):
        assert force_text(label) == 'kielo / {0} [hidden]'.format(
            photo.image_filename())
