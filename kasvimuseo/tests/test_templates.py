# -*- coding: utf-8 -*-
"""Tests for the public-facing report templates.

``test_views.py`` covers the view layer -- context, querysets, status codes.
These tests assert what a visitor or a member of the garden staff actually
reads on the rendered page: names, flowering months, light requirements, beds,
origins, cultivation history, navigation links and the plant blobs of the bed
map.
"""

from __future__ import unicode_literals

import pytest
from django.core.urlresolvers import reverse

from kasvimuseo.templatetags.bush import bush_shadow
from kasvimuseo.templatetags.lightings import lighting_name
from kasvimuseo.templatetags.months import month_name
from kasvimuseo.tests.factories import (create_bed, create_location,
                                        create_planted, create_plot,
                                        create_species)


def page(response):
    """The rendered page as text.

    ``response.content`` is bytes and every one of these templates is Finnish,
    so it has to be decoded before it can be compared with anything.
    """
    assert response.status_code == 200
    return response.content.decode('utf-8')


def month(number):
    """``month_name`` returns a lazy translation proxy; force it to text."""
    return '{0}'.format(month_name(number))


def species_url(name, external_id):
    return reverse(name, kwargs={'species_external_ids': str(external_id)})


# reports/planted-species-list.html


@pytest.mark.django_db
def test_species_list_shows_public_species_ordered_by_finnish_name(client):
    create_planted(name_fi='valkonarsissi', external_id=2)
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='piilokasvi', external_id=3, public=False)

    content = page(client.get(reverse('planted-species-list')))

    assert 'piilokasvi' not in content
    assert content.index('ahdekaunokki') < content.index('valkonarsissi')


@pytest.mark.django_db
def test_species_list_links_to_the_per_species_report(client):
    create_planted(name_fi='ahdekaunokki', external_id=7)

    content = page(client.get(reverse('planted-species-list')))

    assert 'href="{0}"'.format(
        species_url('planted-species-compact', 7)) in content


@pytest.mark.django_db
def test_species_list_omits_a_species_whose_plantings_were_cared_to_zero(
        client):
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='harvennettu', external_id=2, cares=[0])

    content = page(client.get(reverse('planted-species-list')))

    assert 'harvennettu' not in content
    assert 'ahdekaunokki' in content


# reports/planted-species.html on planted-species-base-printable.html


@pytest.fixture
def full_species(photo_factory):
    """A species with everything the per-species sheet can show filled in."""
    species = create_species(name_fi='valkonarsissi',
                             external_id=1,
                             genus='Narcissus',
                             species='poeticus',
                             subspecies='recurvus',
                             flower_color='valkoinen',
                             flowering_start=6,
                             flowering_end=8,
                             lighting=2,
                             substrate='multava',
                             photo=photo_factory(title='valkonarsissi kukassa',
                                                 width=12, height=8))
    planting = create_planted(species=species,
                              external_id=1,
                              nickname='mummon kukka',
                              bed=create_bed(name='3', public=True,
                                             plot=create_plot(name='Piha')))
    observation = planting.observation
    observation.origin = create_location(name='Yläne', village='Kirkonkylä')
    observation.history = 'kasvanut pihassa 1920-luvulta'
    observation.stories = 'mummo poimi niistä kimpun'
    observation.save()
    return species


@pytest.mark.django_db
def test_printable_sheet_shows_the_names_and_the_photo(client, full_species):
    content = page(client.get(species_url('planted-species', 1)))

    assert 'valkonarsissi' in content
    assert 'Narcissus' in content
    assert 'poeticus' in content
    assert 'recurvus' in content
    assert '"mummon kukka"' in content
    assert full_species.photo.get_display_url() in content
    # 12x8: the wider-than-tall branch of the header class
    assert 'class="header horizontal"' in content


@pytest.mark.django_db
def test_printable_sheet_shows_flowering_time_and_light_requirement(
        client, full_species):
    content = page(client.get(species_url('planted-species', 1)))

    # Month names come from Django's translated ``MONTHS``; ask the filter
    # rather than hardcoding the Finnish catalog.
    assert '{0}–{1}'.format(month(6), month(8)) in content
    assert '{0}'.format(lighting_name(2)) in content
    assert 'valkoinen' in content
    assert 'multava' in content


@pytest.mark.django_db
def test_printable_sheet_collapses_a_single_month_flowering_time(client,
                                                                full_species):
    full_species.flowering_end = 6
    full_species.save()

    content = page(client.get(species_url('planted-species', 1)))

    assert month(6) in content
    assert '{0}–'.format(month(6)) not in content


@pytest.mark.django_db
def test_printable_sheet_shows_beds_origins_and_cultivation_history(
        client, full_species):
    content = page(client.get(species_url('planted-species', 1)))

    assert 'Piha' in content
    assert '3' in content
    assert 'Yläne' in content
    assert 'Kirkonkylä' in content
    assert 'kasvanut pihassa 1920-luvulta' in content
    assert 'mummo poimi niistä kimpun' in content
    # The origin-information heading is pluralised off ``page.origins``
    assert 'alkuperäiseltä' in content
    assert 'kasvupaikalta' in content


@pytest.mark.django_db
def test_printable_sheet_hides_the_history_of_an_observation_without_texts(
        client, full_species):
    observation = full_species.observation_set.get()
    observation.history = ''
    observation.stories = ''
    observation.save()

    content = page(client.get(species_url('planted-species', 1)))

    assert '<dt>' not in content


@pytest.mark.django_db
def test_printable_sheet_renders_a_bare_species_cleanly(client):
    """No photo, no nickname, no flowering months -- every empty branch."""
    species = create_species(name_fi='ahdekaunokki', external_id=1,
                             flowering_start=None, flowering_end=None,
                             lighting=None)
    create_planted(species=species, external_id=1, nickname='')

    content = page(client.get(species_url('planted-species', 1)))

    assert 'ahdekaunokki' in content
    assert 'class="local-names"' not in content
    # No photo: both the src and the dimension comment come out empty, and the
    # header falls to the ``vertical`` branch.
    assert '<img src="" />' in content
    assert 'class="header vertical"' in content


# planted-species-base-printable.html navigation


@pytest.mark.django_db
@pytest.mark.parametrize('referer,expected', [
    ('http://example.com/kasvimuseo/edellinen/', True),
    (None, False),
])
def test_printable_next_link_comes_from_the_referer(client, referer, expected):
    create_planted(name_fi='ahdekaunokki', external_id=1)
    create_planted(name_fi='valkonarsissi', external_id=2)
    extra = {'HTTP_REFERER': referer} if referer else {}

    content = page(client.get(species_url('planted-species', 1), **extra))

    assert ('Jatka' in content) is expected
    if expected:
        assert 'href="{0}"'.format(referer) in content


# reports/planted-species-base-compact.html navigation


@pytest.fixture
def three_species(db):
    for external_id, name in enumerate(['ahdekaunokki',
                                        'kissankello',
                                        'valkonarsissi'], start=1):
        create_planted(name_fi=name, external_id=external_id)


@pytest.mark.django_db
@pytest.mark.parametrize('external_id,previous_id,next_id', [
    (1, None, 2),
    (2, 1, 3),
    (3, 2, None),
])
def test_compact_navigation_uses_the_adjacent_species(
        client, three_species, external_id, previous_id, next_id):
    content = page(client.get(species_url('planted-species-compact',
                                          external_id)))

    for adjacent_id in [previous_id, next_id]:
        link = 'href="{0}"'.format(
            species_url('planted-species-compact', adjacent_id or 0))
        assert (link in content) is (adjacent_id is not None)
    assert 'href="{0}"'.format(reverse('planted-species-list')) in content


@pytest.mark.django_db
def test_compact_navigation_names_the_adjacent_species(client, three_species):
    content = page(client.get(species_url('planted-species-compact', 2)))

    assert '(ahdekaunokki)' in content
    assert '(valkonarsissi)' in content
    # The compact base is the one with the previous/next navbar; the printable
    # base has neither.
    assert 'navbar-species-name' in content


# reports/planted-observation.html


@pytest.mark.django_db
def test_observation_page_shows_species_origin_and_beds(client):
    planting = create_planted(
        name_fi='valkonarsissi', external_id=42,
        bed=create_bed(name='3', public=True, plot=create_plot(name='Piha')))
    observation = planting.observation
    observation.origin = create_location(name='Yläne', village='Kirkonkylä')
    observation.variation = 'kerrottu'
    observation.save()

    content = page(client.get(reverse('planted-observation', args=[42])))

    assert 'valkonarsissi, kerrottu' in content
    assert 'Yläne, Kirkonkylä' in content
    assert 'Piha/3' in content
    assert 'Havainto 42' in content


@pytest.mark.django_db
@pytest.mark.parametrize('history,stories,shown,hidden', [
    ('kasvatettu 1920', 'mummon muisto', ['kasvatettu 1920', 'mummon muisto'],
     []),
    ('kasvatettu 1920', '', ['kasvatettu 1920'], ['mummon muisto']),
    ('', 'mummon muisto', ['mummon muisto'], ['kasvatettu 1920']),
    ('', '', [], ['kasvatettu 1920', 'mummon muisto']),
])
def test_observation_page_texts_block(client, history, stories, shown, hidden):
    planting = create_planted(name_fi='valkonarsissi', external_id=42)
    observation = planting.observation
    observation.origin = create_location(name='Yläne', village='Kirkonkylä')
    observation.history = history
    observation.stories = stories
    observation.save()

    content = page(client.get(reverse('planted-observation', args=[42])))

    for text in shown:
        assert '<dd>{0}</dd>'.format(text) in content
    for text in hidden:
        assert text not in content
    # The origin heading of the texts block only appears with texts under it.
    assert ('<dt>Yläne, Kirkonkylä</dt>' in content) is bool(shown)


# kasvimuseo/bed-map.html


@pytest.mark.django_db
def test_bed_map_draws_a_plant_blob_with_the_bush_shadow_css(client):
    planting = create_planted(name_fi='valkonarsissi', external_id=1,
                              width=30, depth=15,
                              distance_left=20, distance_front=10)

    content = page(client.get(reverse('bed-map',
                                      kwargs={'pk': planting.bed_id})))

    assert 'style="{0}"'.format(bush_shadow(planting)) in content
    assert 'left: 20em;' in content
    assert 'bottom: 10em;' in content
    assert 'valkonarsissi' in content
    # ``bed_depth`` is a fixed 40 in the view
    assert 'style="height: 40em;"' in content


@pytest.mark.django_db
def test_bed_map_renders_an_empty_bed(client):
    bed = create_bed(name='tyhjä', public=True)

    content = page(client.get(reverse('bed-map', kwargs={'pk': bed.pk})))

    assert 'tyhjä' in content
    assert 'class="bush"' not in content


# reports/planting-labels.html
#
# The label editor is a client-side Vue application fed by the
# ``planting-label-data`` endpoint (covered in ``test_views.py``). Only the
# server side of that contract can be asserted here; the behaviour of the
# JavaScript itself needs the browser suite.


@pytest.mark.django_db
def test_label_editor_mounts_vue_and_points_at_the_data_endpoint(client):
    content = page(client.get(reverse('planting-label')))

    assert 'id="app"' in content
    assert "el: '#app'" in content
    assert "'{0}'".format(reverse('planting-label-data')) in content
    assert 'vue.min.js' in content


# A species external id that does not exist


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['planted-species',
                                      'planted-species-compact'])
def test_unknown_external_id_renders_an_empty_report(client, url_name):
    """Pins current behaviour; see docs/issues/007."""
    create_planted(name_fi='valkonarsissi', external_id=1)

    content = page(client.get(species_url(url_name, 999999)))

    # No 500, no exception: the queryset is simply empty, so the report has no
    # species blocks and -- in the compact base -- no navigation either.
    assert 'class="species"' not in content
    assert 'valkonarsissi' not in content
