# -*- coding: utf-8 -*-
"""Tests for :mod:`kasvimuseo.views`."""

from __future__ import unicode_literals

import json
from contextlib import contextmanager

import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client

from kasvimuseo.models import Label, Planting, Species
from kasvimuseo.tests.conftest import log_in_as_staff
from kasvimuseo.tests.factories import (create_bed, create_location,
                                        create_observation, create_planted,
                                        create_planting, create_species)
from kasvimuseo.views import PlantedSpecies, PlantedSpeciesPrintable


def label_item(species, external_ids, visible=True, photo_pk=None):
    return {'id': species.pk,
            'photo_pk': photo_pk,
            'visible': visible,
            'external_ids': list(external_ids)}


class QueryCount(object):
    """What :func:`counted_queries` fills in when its block is done."""
    count = None


@contextmanager
def counted_queries():
    """``assertNumQueries`` for a plain pytest function.

    Django 1.5 offers the check on ``TestCase`` only, and has no
    ``CaptureQueriesContext`` to borrow, so do what its
    ``_AssertNumQueriesContext`` does: switch the debug cursor on, and stop the
    test client's ``request_started`` signal from resetting the query log.
    """
    from django.core.signals import request_started
    from django.db import connection, reset_queries

    request_started.disconnect(reset_queries)
    old_debug_cursor = connection.use_debug_cursor
    connection.use_debug_cursor = True
    counted = QueryCount()
    start = len(connection.queries)
    try:
        yield counted
    finally:
        counted.count = len(connection.queries) - start
        connection.use_debug_cursor = old_debug_cursor
        request_started.connect(reset_queries)


# PlantedSpeciesList


@pytest.mark.django_db
def test_planted_species_list_shows_only_public_planted(client):
    """A private bed, a removal and a count of zero each hide a species."""
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='valkonarsissi', external_id=2)
    create_planted(name_fi='piilokasvi', external_id=3, public=False)
    create_planted(name_fi='poistettu', external_id=4, removed=True)
    create_planted(name_fi='harvennettu', external_id=5, cares=[0])

    response = client.get(reverse('planted-species-list'))

    assert response.status_code == 200
    # 'poistettu' used to be listed here: ``SpeciesManager.public_planted``
    # never looked at ``removal_date``, unlike ``Planting.is_public_planted``,
    # which it now uses (issue 001). The page lists what the garden holds now.
    assert [species.name_fi for species in response.context['object_list']] == [
        'ahdekaunokki', 'valkonarsissi']


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
def test_labels_api_get_groups_by_species_and_reports_visibility(staff_client):
    labelled = create_planted(name_fi='ahdekaunokki', external_id=1,
                              nickname='mummon kukka')
    label = Label.objects.create(species=labelled.observation.species,
                                 visible=False)
    labelled.label = label
    labelled.save()
    create_planted(name_fi='valkonarsissi', external_id=2)

    response = staff_client.get(reverse('planting-label-data'))

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
def test_labels_api_get_returns_full_species_shape(staff_client):
    create_planted(name_fi='valkonarsissi', external_id=7)

    response = staff_client.get(reverse('planting-label-data'))
    data = json.loads(response.content.decode('utf-8'))

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
def test_labels_api_get_reads_back_the_label_photo(staff_client, display_size,
                                                   photo_factory):
    """Issue 039: the photo chosen for a label wins over the species photo.

    The read path used to derive the photo from the species alone, so a saved
    ``Label.photo`` was written and never looked at again.
    """
    planting = create_planted(name_fi='valkonarsissi', external_id=1)
    chosen = photo_factory(title='valkonarsissi kukassa')
    # Saved after ``chosen``, so ``autoconnect_photo_to_species`` leaves this
    # one as the species photo: the value the read path handed back regardless
    # of what the label said.
    species_photo = photo_factory(title='valkonarsissi lehdet')
    species = planting.observation.species
    assert Species.objects.get(pk=species.pk).photo_id == species_photo.pk
    label = Label.objects.create(species=species, photo=chosen)
    planting.label = label
    planting.save()

    response = staff_client.get(reverse('planting-label-data'))
    data = json.loads(response.content.decode('utf-8'))

    entry, = data['object_list']
    assert entry['photo_pk'] == chosen.pk
    # Both are still offered as alternatives, so the chevrons can go back.
    assert set(int(pk) for pk in entry['all_photos']) == {chosen.pk,
                                                         species_photo.pk}


@pytest.mark.django_db
def test_labels_api_get_falls_back_to_the_species_photo(staff_client,
                                                        display_size,
                                                        photo_factory):
    """A species with no ``Label`` row, and a label with no photo of its own."""
    unlabelled = create_planted(name_fi='tulppaani', external_id=1)
    labelled = create_planted(name_fi='valkonarsissi', external_id=2)
    tulppaani = photo_factory(title='tulppaani kukassa')
    valkonarsissi = photo_factory(title='valkonarsissi kukassa')
    labelled.label = Label.objects.create(species=labelled.observation.species)
    labelled.save()

    response = staff_client.get(reverse('planting-label-data'))
    data = json.loads(response.content.decode('utf-8'))

    by_name = dict((entry['name_fi'], entry) for entry in data['object_list'])
    assert by_name['tulppaani']['photo_pk'] == tulppaani.pk
    assert by_name['valkonarsissi']['photo_pk'] == valkonarsissi.pk
    assert unlabelled.label is None


@pytest.mark.django_db
def test_labels_api_get_reads_the_label_photo_without_more_queries(
        staff_client, display_size, photo_factory):
    """Reading the photo choice back costs nothing: it rides on the join.

    18 queries for this data before the fix, 16 after it. Preferring
    ``label.photo`` cannot add one -- ``select_related('photo')`` widens the
    ``Label`` query rather than issuing another -- and it saves the deferred
    lookup of ``species.photo`` for each of the two labels that has a photo of
    its own, which is the whole of the difference.

    Issue 012 then took it to 14: ``ObservationManager`` prefetches the beds it
    used to fetch one planting at a time.

    16 now, and the two on top are not this view's: the endpoint is staff-only
    since issue 052, so every request first reads the session row and then the
    user it names. They are what any admin page already pays.
    """
    first = create_planted(name_fi='valkonarsissi', external_id=1)
    second = create_planted(name_fi='tulppaani', external_id=2)
    for planting, title in [(first, 'valkonarsissi kukassa'),
                            (second, 'tulppaani kukassa')]:
        planting.label = Label.objects.create(
            species=planting.observation.species,
            photo=photo_factory(title=title))
        planting.save()
    create_planted(name_fi='ahdekaunokki', external_id=3)

    with counted_queries() as queries:
        response = staff_client.get(reverse('planting-label-data'))

    assert response.status_code == 200
    assert len(json.loads(response.content.decode('utf-8'))
               ['object_list']) == 3
    assert queries.count == 16


@pytest.mark.django_db
def test_labels_api_get_omits_non_public_species(staff_client):
    create_planted(name_fi='piilokasvi', external_id=1, public=False)

    response = staff_client.get(reverse('planting-label-data'))
    data = json.loads(response.content.decode('utf-8'))

    assert data == {'object_list': []}


@pytest.mark.django_db
def test_labels_api_get_orders_the_museum_numbers_on_a_label(staff_client):
    """Issue 053: smallest museum number first, and as a number.

    The handler used to sort the ``Observation`` instances themselves, which
    on Python 2 compares them by address, so the numbers arrived in whatever
    order the objects happened to sit in memory. 2, 11 and 12 tell the two
    wrong answers apart as well: sorted as text they would come back 11, 12,
    2.

    The nicknames are built from the same sequence, so they have to travel
    with their own numbers.
    """
    species = create_species(name_fi='valkonarsissi')
    for external_id, nickname in ((12, 'mummon kukka'),
                                  (2, 'papan kukka'),
                                  (11, 'tädin kukka')):
        create_planted(species=species, external_id=external_id,
                       nickname=nickname)

    data = json.loads(
        staff_client.get(reverse('planting-label-data'))
        .content.decode('utf-8'))

    entry, = data['object_list']
    assert entry['external_ids'] == [2, 11, 12]
    assert entry['nicknames'] == ['papan kukka', 'tädin kukka',
                                  'mummon kukka']


@pytest.mark.django_db
def test_labels_api_get_puts_a_missing_number_first(staff_client):
    """Issue 053: ``external_id`` is nullable, so the order has to say where.

    Nothing in the production dump or in ``browser_tests/seed.py`` is missing
    one, but the column allows it. First is where ``None`` lands in
    ``kasvimuseo_model_tags.external_ids`` and where ``null`` lands in the
    editor's ``insort``, so it is where it lands here.
    """
    species = create_species(name_fi='valkonarsissi')
    create_planted(species=species, external_id=7)
    create_planted(species=species, external_id=None)

    data = json.loads(
        staff_client.get(reverse('planting-label-data'))
        .content.decode('utf-8'))

    entry, = data['object_list']
    assert entry['external_ids'] == [None, 7]


# PlantedSpeciesLabelsApi.post


@pytest.mark.django_db
def test_labels_api_post_links_each_planting_to_its_own_species_label(
        staff_client):
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
    response = staff_client.post(reverse('planting-label-data'),
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

    # Two items naming the same species. The two labels differ in nothing the
    # submitted item can be matched against except the plantings it names, so
    # this is the case a mapping keyed on the species collapses -- issue 010's
    # option 2. Measured against the old handler, pairing by position survived
    # it on PostgreSQL, so this pins the contract rather than reproducing a
    # failure.
    species = remaining[0].observation.species
    twin = create_planting(observation=create_observation(species=species,
                                                          external_id=9),
                           bed=create_bed(name='2'))
    items = [label_item(species, [remaining[0].observation.external_id]),
             label_item(species, [9], visible=False)]
    response = staff_client.post(reverse('planting-label-data'),
                           data=json.dumps(items),
                           content_type='application/json')

    assert response.status_code == 200
    assert Label.objects.count() == 2
    first_label = Planting.objects.get(pk=remaining[0].pk).label
    second_label = Planting.objects.get(pk=twin.pk).label
    assert first_label.pk != second_label.pk
    assert (first_label.visible, second_label.visible) == (True, False)


@pytest.mark.django_db
def test_labels_api_post_survives_a_get_round_trip(staff_client):
    planting = create_planted(name_fi='valkonarsissi', external_id=3)
    species = planting.observation.species

    staff_client.post(reverse('planting-label-data'),
                data=json.dumps([label_item(species, [3], visible=False)]),
                content_type='application/json')
    response = staff_client.get(reverse('planting-label-data'))
    data = json.loads(response.content.decode('utf-8'))

    entry, = data['object_list']
    assert entry['id'] == species.pk
    assert entry['visible'] is False
    assert entry['external_ids'] == [3]


@pytest.mark.django_db
def test_labels_api_post_round_trips_the_museum_numbers_in_order(staff_client):
    """Issue 053, the half a saved label reaches.

    Once a ``Label`` exists the numbers come from its plantings rather than
    from the grouped queryset, and ``Planting.Meta.ordering`` orders by the
    species name, which says nothing about two plantings of the same species.
    Post them out of order -- what dragging a number in the editor does -- and
    the sheet still has to read 2, 11, 12.
    """
    species = create_species(name_fi='valkonarsissi')
    for external_id in (12, 2, 11):
        create_planted(species=species, external_id=external_id)

    staff_client.post(reverse('planting-label-data'),
                      data=json.dumps([label_item(species, [12, 2, 11])]),
                      content_type='application/json')
    data = json.loads(
        staff_client.get(reverse('planting-label-data'))
        .content.decode('utf-8'))

    entry, = data['object_list']
    assert Label.objects.count() == 1
    assert entry['external_ids'] == [2, 11, 12]


@pytest.mark.django_db
def test_labels_api_post_round_trips_the_photo_choice(staff_client,
                                                      display_size,
                                                      photo_factory):
    """Issue 039, end to end: POST a photo choice, GET it back.

    This is the test the issue says was missing, and is why the defect survived
    eight years: the ``visible`` flag beside the photo did round-trip, so saving
    looked like it worked.
    """
    planting = create_planted(name_fi='valkonarsissi', external_id=3)
    chosen = photo_factory(title='valkonarsissi kukassa')
    # Saved last, so this is what the species points at.
    species_photo = photo_factory(title='valkonarsissi lehdet')
    species = planting.observation.species

    staff_client.post(reverse('planting-label-data'),
                data=json.dumps([label_item(species, [3],
                                            photo_pk=chosen.pk)]),
                content_type='application/json')
    response = staff_client.get(reverse('planting-label-data'))
    data = json.loads(response.content.decode('utf-8'))

    assert Label.objects.get().photo_id == chosen.pk
    entry, = data['object_list']
    assert entry['photo_pk'] == chosen.pk
    assert entry['photo_pk'] != species_photo.pk


@pytest.mark.django_db(transaction=True)
def test_labels_api_post_keeps_the_old_labels_when_the_save_fails(client,
                                                                 monkeypatch):
    """Issue 010: the delete-and-recreate is one transaction.

    The handler deletes every label before writing the replacements, so a
    failure part way through used to leave the table empty.

    ``transaction=True`` is what makes this a test of the real thing rather
    than of a savepoint: it gives the view a connection nobody else has a
    transaction open on, so the rollback it asks for is the database's.

    It used to be the only thing that made the test observable at all. The
    handler was decorated with ``commit_on_success``, and Django's ``TestCase``
    nops ``transaction.commit`` and ``transaction.rollback`` for the length of
    a test -- 1.5 did, and 1.6 still does, under a comment saying it goes when
    the legacy transaction management does -- so under the ordinary
    ``django_db`` mark the decorator did nothing. ``atomic`` is not nopped
    (upgrade plan Stage 3), so it would now nest as a savepoint and this would
    pass either way.
    """
    staff_client = log_in_as_staff(client)
    planting = create_planted(name_fi='valkonarsissi', external_id=3)
    species = planting.observation.species
    kept = Label.objects.create(species=species, visible=False)

    def fail(*args, **kwargs):
        raise RuntimeError('the save failed half way through')

    monkeypatch.setattr(Planting, 'save', fail)
    with pytest.raises(RuntimeError):
        staff_client.post(reverse('planting-label-data'),
                          data=json.dumps([label_item(species, [3])]),
                          content_type='application/json')

    label = Label.objects.get()
    assert (label.pk, label.visible) == (kept.pk, False)


@pytest.mark.django_db
def test_labels_api_post_ignores_non_public_plantings(staff_client):
    planting = create_planted(name_fi='piilokasvi', external_id=1,
                              public=False)
    species = planting.observation.species

    staff_client.post(reverse('planting-label-data'),
                      data=json.dumps([label_item(species, [1])]),
                      content_type='application/json')

    assert Label.objects.count() == 1
    assert Planting.objects.get(pk=planting.pk).label is None


# The staff gate on both label URLs (issue 052)


@pytest.mark.django_db
@pytest.mark.parametrize('method', ['get', 'post'])
def test_labels_api_refuses_anyone_who_is_not_staff(client, method):
    """Anonymous, then logged in without staff rights. Both are refused.

    Until this gate existed, ``post`` was reachable by anyone who knew the
    URL, and it opens with ``Label.objects.all().delete()``: one request from
    outside emptied the table. 403 rather than the admin's login form, because
    the caller is axios and a login page behind a 200 reads as a saved sheet.
    """
    planting = create_planted(name_fi='valkonarsissi', external_id=1)
    species = planting.observation.species
    Label.objects.create(species=species)
    body = dict(data=json.dumps([label_item(species, [1])]),
                content_type='application/json') if method == 'post' else {}

    response = getattr(client, method)(reverse('planting-label-data'), **body)

    assert response.status_code == 403
    assert Label.objects.count() == 1

    user = User.objects.create_user('vierailija', 'v@invalid', 'salasana')
    assert not user.is_staff
    client.login(username='vierailija', password='salasana')

    response = getattr(client, method)(reverse('planting-label-data'), **body)

    assert response.status_code == 403
    assert Label.objects.count() == 1


@pytest.mark.django_db
def test_the_label_editor_page_shows_a_login_form_to_anyone_else(staff_client):
    """The page is gated the admin's way, which in Django 1.5 is a 200.

    ``staff_member_required`` renders the admin login form at the requested
    URL rather than redirecting -- the register notes that under "Observations,
    not actionable" -- so the assertion is on what came back, not on a status.
    """
    create_planted(name_fi='valkonarsissi', external_id=1)

    anonymous = Client().get(reverse('planting-label'))

    assert 'id="app"' not in anonymous.content.decode('utf-8')
    assert 'name="password"' in anonymous.content.decode('utf-8')
    assert 'id="app"' in staff_client.get(
        reverse('planting-label')).content.decode('utf-8')


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
