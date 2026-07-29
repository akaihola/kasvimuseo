# -*- coding: utf-8 -*-
"""Tests for :mod:`kasvimuseo.views`."""

from __future__ import unicode_literals

import json

import pytest
from django.core.urlresolvers import reverse

from kasvimuseo.models import Label, Planting, Species
from kasvimuseo.tests.factories import (create_bed, create_location,
                                        create_observation, create_planted,
                                        create_planting, create_species)
from kasvimuseo.views import PlantedSpecies, PlantedSpeciesPrintable


def label_item(species, external_ids, visible=True):
    return {'id': species.pk,
            'photo_pk': None,
            'visible': visible,
            'external_ids': list(external_ids)}


# PlantedSpeciesList


@pytest.mark.django_db
def test_planted_species_list_shows_only_public_planted(client):
    """Pins current behaviour; see docs/issues/001."""
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='valkonarsissi', external_id=2)
    create_planted(name_fi='piilokasvi', external_id=3, public=False)
    create_planted(name_fi='poistettu', external_id=4, removed=True)
    create_planted(name_fi='harvennettu', external_id=5, cares=[0])

    response = client.get(reverse('planted-species-list'))

    assert response.status_code == 200
    # Pinned as-is, and 'poistettu' is a defect: unlike
    # ``Planting.is_public_planted``, ``SpeciesManager.public_planted`` never
    # looks at ``removal_date``, so a species whose only planting has been
    # removed is still listed. Only a private bed or a last care operation
    # counting down to zero hides a species here.
    assert [species.name_fi for species in response.context['object_list']] == [
        'ahdekaunokki', 'poistettu', 'valkonarsissi']


@pytest.mark.django_db
def test_planted_species_list_deduplicates_species(client):
    species = create_species(name_fi='valkonarsissi', external_id=1)
    create_planted(species=species, external_id=1)
    create_planting(observation=create_observation(species=species),
                    bed=create_bed(name='2'))

    response = client.get(reverse('planted-species-list'))

    assert [s.pk for s in response.context['object_list']] == [species.pk]


# PlantedSpeciesLabelsApi.get


@pytest.mark.django_db
def test_labels_api_get_groups_by_species_and_reports_visibility(client):
    labelled = create_planted(name_fi='ahdekaunokki', external_id=1,
                              nickname='mummon kukka')
    label = Label.objects.create(species=labelled.observation.species,
                                 visible=False)
    labelled.label = label
    labelled.save()
    create_planted(name_fi='valkonarsissi', external_id=2)

    response = client.get(reverse('planting-label-data'))

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    data = json.loads(response.content.decode('utf-8'))
    by_name = dict((entry['name_fi'], entry) for entry in data['object_list'])
    assert sorted(by_name) == ['ahdekaunokki', 'valkonarsissi']
    # The species that has a Label keeps that label's ``visible`` flag and
    # takes its observations from the plantings linked to the label.
    assert by_name['ahdekaunokki']['visible'] is False
    assert by_name['ahdekaunokki']['external_ids'] == [1]
    assert by_name['ahdekaunokki']['nicknames'] == ['mummon kukka']
    # The species without a Label is appended, always visible.
    assert by_name['valkonarsissi']['visible'] is True
    assert by_name['valkonarsissi']['external_ids'] == [2]


@pytest.mark.django_db
def test_labels_api_get_returns_full_species_shape(client):
    create_planted(name_fi='valkonarsissi', external_id=7)

    data = json.loads(
        client.get(reverse('planting-label-data')).content.decode('utf-8'))

    entry, = data['object_list']
    assert sorted(entry) == ['all_photos', 'external_ids', 'genus', 'group',
                             'id', 'name_fi', 'nicknames', 'photo_pk',
                             'species', 'subspecies', 'visible']
    assert entry['id'] == Species.objects.get().pk
    assert entry['genus'] == 'Narcissus'
    assert entry['species'] == 'poeticus'
    assert entry['photo_pk'] is None
    assert entry['all_photos'] == {}


@pytest.mark.django_db
def test_labels_api_get_omits_non_public_species(client):
    create_planted(name_fi='piilokasvi', external_id=1, public=False)

    data = json.loads(
        client.get(reverse('planting-label-data')).content.decode('utf-8'))

    assert data == {'object_list': []}


# PlantedSpeciesLabelsApi.post


@pytest.mark.django_db
def test_labels_api_post_links_each_planting_to_its_own_species_label(client):
    """Round-trip with several items and non-sequential species primary keys.

    The view re-links plantings via ``zip(items, labels)``, i.e. it assumes
    ``bulk_create`` inserts in input order and that ``order_by('pk')`` hands
    the rows back in that same order. Post the items in an order that does not
    match the species primary keys, so a positional mismatch shows up.
    """
    plantings = [create_planted(name_fi='kasvi{0}'.format(index),
                                external_id=index)
                 for index in range(1, 6)]
    # Punch holes in the primary key sequence.
    Species.objects.filter(
        pk__in=[plantings[1].observation.species_id,
                plantings[3].observation.species_id]).delete()
    remaining = [plantings[0], plantings[2], plantings[4]]
    assert Planting.objects.count() == 3
    Label.objects.create(species=remaining[0].observation.species)

    items = [label_item(planting.observation.species,
                        [planting.observation.external_id],
                        visible=(index != 1))
             # posted newest species first, i.e. descending primary key
             for index, planting in enumerate(reversed(remaining))]
    response = client.post(reverse('planting-label-data'),
                           data=json.dumps(items),
                           content_type='application/json')

    assert response.status_code == 200
    assert response.content.decode('utf-8') == 'OK'
    # The pre-existing label was replaced, not added to.
    assert Label.objects.count() == 3
    for planting in remaining:
        planting = Planting.objects.get(pk=planting.pk)
        assert planting.label is not None
        assert planting.label.species_id == planting.observation.species_id
    # The ``visible`` flag travelled with the right species, too.
    visible_by_species = dict(
        (label.species_id, label.visible) for label in Label.objects.all())
    assert visible_by_species == {
        remaining[0].observation.species_id: True,
        remaining[1].observation.species_id: False,
        remaining[2].observation.species_id: True}


@pytest.mark.django_db
def test_labels_api_post_survives_a_get_round_trip(client):
    planting = create_planted(name_fi='valkonarsissi', external_id=3)
    species = planting.observation.species

    client.post(reverse('planting-label-data'),
                data=json.dumps([label_item(species, [3], visible=False)]),
                content_type='application/json')
    data = json.loads(
        client.get(reverse('planting-label-data')).content.decode('utf-8'))

    entry, = data['object_list']
    assert entry['id'] == species.pk
    assert entry['visible'] is False
    assert entry['external_ids'] == [3]


@pytest.mark.django_db
def test_labels_api_post_ignores_non_public_plantings(client):
    planting = create_planted(name_fi='piilokasvi', external_id=1,
                              public=False)
    species = planting.observation.species

    client.post(reverse('planting-label-data'),
                data=json.dumps([label_item(species, [1])]),
                content_type='application/json')

    assert Label.objects.count() == 1
    assert Planting.objects.get(pk=planting.pk).label is None


# PlantedSpecies.get_context_data


@pytest.mark.django_db
def test_get_context_data_adjacency_at_both_ends_of_the_alphabet():
    for index, name in enumerate(['ahdekaunokki', 'mesiangervo',
                                  'valkonarsissi'], start=1):
        create_planted(name_fi=name, external_id=index)
    view = PlantedSpeciesPrintable()

    contexts = dict(
        (name, view.get_context_data(
            Species.objects.filter(name_fi=name))['pages'][0])
        for name in ['ahdekaunokki', 'mesiangervo', 'valkonarsissi'])

    assert contexts['ahdekaunokki']['previous'] is None
    assert contexts['ahdekaunokki']['next'].name_fi == 'mesiangervo'
    assert contexts['mesiangervo']['previous'].name_fi == 'ahdekaunokki'
    assert contexts['mesiangervo']['next'].name_fi == 'valkonarsissi'
    assert contexts['valkonarsissi']['previous'].name_fi == 'mesiangervo'
    assert contexts['valkonarsissi']['next'] is None


@pytest.mark.django_db
def test_get_context_data_uses_the_base_template_of_the_subclass():
    context = PlantedSpeciesPrintable().get_context_data(
        Species.objects.none())

    assert context['pages'] == []
    assert context['base_template'] == (
        'kasvimuseo/reports/planted-species-base-printable.html')


@pytest.mark.django_db
def test_get_context_data_lists_only_public_beds():
    species = create_species(name_fi='valkonarsissi', external_id=1)
    public_bed = create_bed(name='julkinen', public=True)
    private_bed = create_bed(name='salainen', public=False)
    create_planted(species=species, bed=public_bed, external_id=1)
    create_planted(species=species, bed=private_bed, external_id=2)

    page = PlantedSpeciesPrintable().get_context_data(
        Species.objects.filter(pk=species.pk))['pages'][0]

    assert [bed.pk for bed in page['beds']] == [public_bed.pk]
    assert [planting.bed_id for planting in page['beds'][0].plantings] == [
        public_bed.pk]


@pytest.mark.django_db
def test_get_context_data_bed_plantings_exclude_removed_ones():
    species = create_species(name_fi='valkonarsissi', external_id=1)
    bed = create_bed(name='julkinen', public=True)
    kept = create_planted(species=species, bed=bed, external_id=1)
    create_planted(species=species, bed=bed, external_id=2, removed=True)

    page = PlantedSpeciesPrintable().get_context_data(
        Species.objects.filter(pk=species.pk))['pages'][0]

    assert [planting.pk for planting in page['beds'][0].plantings] == [kept.pk]


@pytest.mark.django_db
def test_get_context_data_deduplicates_origins_and_skips_empty_nicknames():
    species = create_species(name_fi='valkonarsissi', external_id=1)
    origin = create_location(name='Talo')
    other_origin = create_location(name='Aitta')
    create_planting(observation=create_observation(
        species=species, origin=origin, external_id=1, nickname='mummon'))
    create_planting(observation=create_observation(
        species=species, origin=origin, external_id=2, nickname=''))
    create_planting(observation=create_observation(
        species=species, origin=other_origin, external_id=3,
        nickname='papan'))

    page = PlantedSpeciesPrintable().get_context_data(
        Species.objects.filter(pk=species.pk))['pages'][0]

    assert page['origins'] == set(['Talo', 'Aitta'])
    assert sorted(page['local_names']) == ['mummon', 'papan']
    assert len(page['planted_observations']) == 3


# PlantedSpecies.get


@pytest.mark.django_db
def test_get_without_referer_leaves_next_as_the_adjacent_species(rf):
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='valkonarsissi', external_id=2)

    response = PlantedSpeciesPrintable.as_view()(
        rf.get('/kasvimuseo/planted-species-printable/1/'),
        species_external_ids='1')

    assert 'next' not in response.context_data
    assert response.context_data['pages'][0]['next'].name_fi == 'valkonarsissi'


@pytest.mark.django_db
def test_get_with_referer_overwrites_the_top_level_next_with_a_url(rf):
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='valkonarsissi', external_id=2)

    response = PlantedSpeciesPrintable.as_view()(
        rf.get('/kasvimuseo/planted-species-printable/1/',
               HTTP_REFERER='http://example.com/kasvimuseo/edellinen/'),
        species_external_ids='1')

    # Pinned as-is: the top-level ``next`` is a URL string, while the page
    # dict the templates actually read still holds a Species.
    assert response.context_data['next'] == (
        'http://example.com/kasvimuseo/edellinen/')
    assert response.context_data['pages'][0]['next'].name_fi == 'valkonarsissi'


@pytest.mark.django_db
def test_get_renders_every_requested_external_id(rf):
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='valkonarsissi', external_id=2)

    response = PlantedSpeciesPrintable.as_view()(
        rf.get('/kasvimuseo/planted-species-printable/1,2/'),
        species_external_ids='1,2')

    assert [page['species'].name_fi for page in response.context_data['pages']] == [
        'ahdekaunokki', 'valkonarsissi']


def test_planted_species_has_no_base_template_of_its_own():
    assert not hasattr(PlantedSpecies, 'base_template_name')


# planted_observation


@pytest.mark.django_db
def test_planted_observation_404s_for_an_unknown_external_id(client):
    response = client.get(reverse('planted-observation', args=[999999]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_planted_observation_404s_when_no_observation_carries_the_number(client):
    """An unknown number still 404s once other observations exist."""
    create_planted(name_fi='valkonarsissi', external_id=42)

    response = client.get(reverse('planted-observation', args=[43]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_planted_observation_renders_the_first_of_a_duplicated_number(client):
    """A shared museum number is a page, not a 500; see docs/issues/041."""
    first = create_planted(name_fi='valkonarsissi', external_id=147)
    second = create_planted(name_fi='ahdekaunokki', external_id=147)
    assert first.observation_id < second.observation_id

    responses = [client.get(reverse('planted-observation', args=[147]))
                 for _ in range(2)]

    # Deterministically the lower primary key, on every request: the view
    # orders explicitly rather than leaving it to the database.
    assert [response.status_code for response in responses] == [200, 200]
    assert [response.context['observation'].pk for response in responses] == [
        first.observation_id, first.observation_id]
    assert [response.context['species'].name_fi for response in responses] == [
        'valkonarsissi', 'valkonarsissi']


@pytest.mark.django_db
@pytest.mark.parametrize('history,stories,expected', [
    ('', '', []),
    ('kasvatettu 1920', '', ['kasvatettu 1920']),
    ('', 'mummon muisto', ['mummon muisto']),
    ('kasvatettu 1920', 'mummon muisto',
     ['kasvatettu 1920', 'mummon muisto']),
])
def test_planted_observation_texts(client, history, stories, expected):
    planting = create_planted(name_fi='valkonarsissi', external_id=42)
    observation = planting.observation
    observation.history = history
    observation.stories = stories
    observation.save()

    response = client.get(reverse('planted-observation', args=[42]))

    assert response.status_code == 200
    assert response.context['texts'] == expected
    assert [bed.pk for bed in response.context['beds']] == [planting.bed_id]
    assert response.context['species'].name_fi == 'valkonarsissi'


# BedMap


@pytest.mark.django_db
def test_bed_map_puts_bed_depth_in_the_context(client):
    planting = create_planted(name_fi='valkonarsissi', external_id=1)

    response = client.get(reverse('bed-map', kwargs={'pk': planting.bed_id}))

    assert response.status_code == 200
    assert response.context['bed_depth'] == 40
    assert response.context['object'].pk == planting.bed_id
    assert 'valkonarsissi' in response.content.decode('utf-8')


# The report templates, which open the image files


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['planted-species',
                                      'planted-species-compact'])
def test_report_renders_with_real_media(client, photo_factory, url_name):
    species = create_species(name_fi='valkonarsissi', external_id=1)
    species.photo = photo_factory(title='valkonarsissi kukassa')
    species.save()
    create_planted(species=species, external_id=1)

    response = client.get(
        reverse(url_name, kwargs={'species_external_ids': '1'}))

    assert response.status_code == 200
    assert 'valkonarsissi' in response.content.decode('utf-8')
