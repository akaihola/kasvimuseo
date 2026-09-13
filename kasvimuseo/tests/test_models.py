# -*- coding: utf-8 -*-
"""Tests for ``kasvimuseo.models``, above all the public-visibility rules."""

from __future__ import unicode_literals

import datetime

import pytest
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import override

from kasvimuseo import models
from kasvimuseo.tests.factories import (create_bed, create_care,
                                        create_label, create_location,
                                        create_observation, create_planted,
                                        create_planting, create_plot,
                                        create_species)
from kasvimuseo.tests.test_views import counted_queries


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
    assert list(models.Species.objects.public_planted()) == []
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
def test_public_planted_query_count_does_not_grow_with_the_plantings():
    """Issue 012: the three managers must not query per planting.

    ``ObservationManager`` used to fetch ``planting.bed`` one row at a time --
    ``is_public_planted`` reads ``bed.public``, and only ``PlantingManager``
    had the matching ``select_related``. The prefetched ``care_set.count()``
    the issue blamed is free: Django 1.5 answers it from ``_result_cache``.

    Before the fix ``Observation`` cost 6 queries for 2 plantings and 10 for 6
    -- one bed each. After it, every manager costs the same for both.

    ``Species`` costs one query more than it did under issue 012 -- 6 rather
    than 5 -- because issue 001 made it read the bed too, and its prefetch is
    what keeps that one query instead of one per planting. Flat is the
    property being pinned here; the constant moved once, deliberately.
    """
    def counts():
        totals = {}
        for name, manager in [('species', models.Species.objects),
                              ('observation', models.Observation.objects),
                              ('planting', models.Planting.objects)]:
            with counted_queries() as queries:
                list(manager.public_planted())
            totals[name] = queries.count
        return totals

    for index in range(2):
        create_planted(name_fi='laji%d' % index, external_id=index + 1)
    two_plantings = counts()
    for index in range(2, 6):
        create_planted(name_fi='laji%d' % index, external_id=index + 1)
    six_plantings = counts()

    assert two_plantings == {'species': 6, 'observation': 5, 'planting': 3}
    assert six_plantings == two_plantings


@pytest.mark.django_db
def test_is_public_planted_unprefetched_is_correct_and_no_more_expensive():
    """A lone ``Planting`` -- no manager, no prefetch -- is the other path.

    Issue 012 warns that consuming a prefetch cache can pessimise this one.
    It does not: ``last_care`` replaces a ``COUNT`` that was followed by the
    same row fetch anyway, so a planting with care records costs one query
    fewer than before, and ``removal_date`` still short circuits ahead of it.
    """
    cases = [('no cares', dict(cares=()), True, 2),
             ('last care above zero', dict(cares=(3, 5)), True, 2),
             ('last care zero', dict(cares=(3, 0)), False, 2),
             # Short circuit: the bed is read, the care records are not.
             ('removed', dict(cares=(3,), removed=True), False, 1)]
    for index, (label, kwargs, expected, queries) in enumerate(cases):
        pk = create_planted(name_fi='laji%d' % index, external_id=index + 1,
                            **kwargs).pk
        planting = models.Planting.objects.get(pk=pk)
        assert not hasattr(planting, '_prefetched_objects_cache')
        with counted_queries() as counted:
            result = planting.is_public_planted()
        assert result is expected, label
        assert counted.count == queries, label


@pytest.mark.django_db
def test_public_planted_picks_only_the_visible_rows():
    visible = create_planted(name_fi='valkonarsissi')
    create_planted(name_fi='keltanarsissi', cares=[0])
    create_planted(name_fi='sinivuokko', public=False)
    create_planted(name_fi='kielo', removed=True)
    assert list(models.Planting.objects.public_planted()) == [visible]
    # 'kielo' is removed, so it is out of the species list too; the three
    # managers agree row for row (issue 001). See
    # test_species_manager_honours_removal_date_and_the_bed.
    assert [s.name_fi for s in models.Species.objects.public_planted()] == [
        'valkonarsissi']


@pytest.mark.django_db
def test_species_visible_when_only_one_of_its_plantings_is():
    species = create_species()
    hidden = create_planted(species=species, cares=[0])
    visible = create_planted(species=species)
    assert hidden.observation.species == visible.observation.species
    assert list(models.Species.objects.public_planted()) == [species]


@pytest.mark.django_db
def test_species_manager_honours_removal_date_and_the_bed():
    """Issue 001: the species list says "holds it now", like the other two.

    ``SpeciesManager`` used to skip ``removal_date`` entirely, and its inner
    loop asked about every planting of the species -- including the ones in
    private beds -- so a species whose public plantings had all been removed
    stayed on the public list, kept there by a planting nobody may see. All
    three managers now apply ``Planting.is_public_planted``.
    """
    removed = create_planted(removed=True, cares=[4])
    assert list(models.Species.objects.public_planted()) == []
    assert list(models.Planting.objects.public_planted()) == []
    assert list(models.Observation.objects.public_planted()) == []

    # The same species, still growing where the public cannot see it. The
    # species reaches the loop on its removed *public* planting, so this is
    # the private planting that used to keep it listed.
    create_planted(species=removed.observation.species, public=False)
    assert list(models.Species.objects.public_planted()) == []
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
    """``ObservationForm`` computes the hint when the form is built.

    The hint left the model field at upgrade plan Stage 5:
    ``get_next_observation_extid`` in ``models.py`` says why it cannot be the
    field's ``help_text`` any more.
    """
    from kasvimuseo.forms import ObservationForm

    form = ObservationForm()
    with override(None):
        assert force_text(form.fields['external_id'].help_text) == \
            'Next available ID: 1'


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
# Model text
# --------------------------------------------------------------------------

@pytest.mark.django_db
def test_model_strings_preserve_finnish_text():
    species = create_species(name_fi='päivänkakkara')
    location = create_location(name='Mäkelä')
    contact = models.Contact(last_name='Hämäläinen', first_name='Päivi')
    observation = create_observation(species=species, origin=location)
    planting = create_planting(observation=observation)
    plot = models.Plot(name='Yläpiha')
    objects = [species, location, contact, observation, planting, plot,
               models.LocationContact(location=location, contact=contact),
               models.Bed(plot=plot, name='itä'),
               models.Label(species=species),
               create_care(planting, count=1, date=DATE, description='lisäys')]
    for obj in objects:
        text = force_text(obj)
        assert 'ä' in text
        expected = text.encode('utf-8') if six.PY2 else text
        assert str(obj) == expected


def test_species_unicode():
    assert force_text(models.Species(name_fi='päivänkakkara')) == 'päivänkakkara'


def test_plot_unicode():
    assert force_text(models.Plot(name='Yläpiha')) == 'Yläpiha'


def test_bed_unicode_without_plot():
    assert force_text(models.Bed(name='1')) == '1'


def test_bed_unicode_with_plot():
    assert force_text(models.Bed(plot=models.Plot(name='Yläpiha'),
                                 name='1')) == 'Yläpiha/1'


def test_contact_unicode():
    assert force_text(models.Contact(last_name='Hämäläinen',
                                     first_name='Maija')) == 'Hämäläinen, Maija'


def test_location_unicode():
    assert force_text(models.Location(name='Mäkelä')) == 'Mäkelä'


@pytest.mark.django_db
def test_location_contact_unicode():
    location = create_location(name='Mäkelä')
    contact = models.Contact.objects.create(last_name='Hämäläinen',
                                            first_name='Maija')
    link = models.LocationContact.objects.create(location=location,
                                                 contact=contact)
    assert force_text(link) == 'Mäkelä/Hämäläinen, Maija'


@pytest.mark.django_db
def test_observation_unicode_without_variation():
    observation = create_observation(species=create_species(name_fi='päivänkakkara'),
                                     origin=create_location(name='Mäkelä'))
    assert force_text(observation) == 'päivänkakkara (Mäkelä)'


@pytest.mark.django_db
def test_observation_unicode_with_variation():
    observation = create_observation(species=create_species(name_fi='päivänkakkara'),
                                     origin=create_location(name='Mäkelä'),
                                     variation='valkoinen')
    assert force_text(observation) == 'päivänkakkara/valkoinen (Mäkelä)'


@pytest.mark.django_db
def test_planting_unicode():
    planting = create_planted(name_fi='päivänkakkara')
    assert force_text(planting) == force_text(planting.observation)


@pytest.mark.django_db
def test_planting_photo_unicode():
    planting = create_planted(name_fi='päivänkakkara')
    photo = models.PlantingPhoto.objects.create(
        planting=planting,
        photo='planting.jpg',
        date=DATE,
        photographer='Maija')
    assert force_text(photo) == '{0}: {1}'.format(
        force_text(planting), force_text(planting.observation))


@pytest.mark.django_db
def test_care_unicode():
    planting = create_planted(name_fi='päivänkakkara')
    care = create_care(planting, count=1, date=DATE, description='kastelu')
    assert force_text(care) == '{0}: {1} / kastelu'.format(
        DATE, force_text(planting))


@pytest.mark.django_db
def test_label_unicode_without_photo():
    label = models.Label.objects.create(species=create_species(name_fi='päivänkakkara'))
    assert force_text(label) == 'päivänkakkara'


@pytest.mark.django_db
def test_label_unicode_hidden_without_photo():
    label = models.Label.objects.create(species=create_species(name_fi='päivänkakkara'),
                                        visible=False)
    with override(None):
        assert force_text(label) == 'päivänkakkara [hidden]'


@pytest.mark.django_db
def test_label_unicode_with_photo(photo_factory):
    photo = photo_factory(title='päivänkakkara kukassa')
    label = models.Label.objects.create(species=create_species(name_fi='päivänkakkara'),
                                        photo=photo)
    assert force_text(label) == 'päivänkakkara / {0}'.format(photo.image_filename())


@pytest.mark.django_db
def test_label_unicode_with_photo_hidden(photo_factory):
    photo = photo_factory(title='päivänkakkara kukassa')
    label = models.Label.objects.create(species=create_species(name_fi='päivänkakkara'),
                                        photo=photo, visible=False)
    with override(None):
        assert force_text(label) == 'päivänkakkara / {0} [hidden]'.format(
            photo.image_filename())


# --------------------------------------------------------------------------
# on_delete on the nullable foreign keys (issue 072)
# --------------------------------------------------------------------------
# Delete the row a nullable ForeignKey points at. The row that points must
# survive, with the field set to None. Issue 072 states the rule.

@pytest.mark.django_db
def test_delete_photo_keeps_the_species(photo_factory):
    photo = photo_factory()
    species = create_species(photo=photo)

    photo.delete()

    species = models.Species.objects.get(pk=species.pk)
    assert species.photo is None


@pytest.mark.django_db
def test_delete_photo_keeps_the_label(photo_factory):
    photo = photo_factory()
    label = create_label(photo=photo)

    photo.delete()

    label = models.Label.objects.get(pk=label.pk)
    assert label.photo is None


@pytest.mark.django_db
def test_delete_plot_keeps_the_bed():
    plot = create_plot()
    bed = create_bed(plot=plot)

    plot.delete()

    bed = models.Bed.objects.get(pk=bed.pk)
    assert bed.plot is None
