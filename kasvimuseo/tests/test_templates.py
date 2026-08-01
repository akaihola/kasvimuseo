# -*- coding: utf-8 -*-
"""Tests for the public-facing report templates.

``test_views.py`` covers the view layer -- context, querysets, status codes.
These tests assert what a visitor or a member of the garden staff actually
reads on the rendered page: names, flowering months, light requirements, beds,
origins, cultivation history, navigation links and the plant blobs of the bed
map.
"""

from __future__ import unicode_literals

import os
import re

import pytest
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

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


@pytest.mark.django_db
def test_species_list_offers_the_jquery_mobile_search_box(client):
    """The filter attributes were ``X``-prefixed and inert; see issues/005."""
    create_planted(name_fi='ahdekaunokki', external_id=1)

    content = page(client.get(reverse('planted-species-list')))

    assert 'Xdata-filter' not in content
    assert 'data-filter="true"' in content
    assert 'data-filter-placeholder="Etsi kasvin nimellä..."' in content
    assert 'data-filter-theme="b"' in content


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
def test_printable_sheet_uses_the_vertical_header_for_a_portrait_photo(
        client, photo_factory):
    """The other branch of the header class; see docs/issues/011.

    ``full_species`` is 12x8, so it only ever exercises ``horizontal``.
    """
    species = create_species(name_fi='valkonarsissi', external_id=1,
                             photo=photo_factory(title='valkonarsissi seisoo',
                                                 width=8, height=12))
    create_planted(species=species, external_id=1)

    content = page(client.get(species_url('planted-species', 1)))

    assert 'class="header vertical"' in content


@pytest.mark.django_db
@pytest.mark.parametrize('width,height,expected', [
    (12, 8, 'horizontal'),
    (8, 12, 'vertical'),
    # A square photo is not wider than it is tall, so it takes the same branch
    # a missing one does.
    (8, 8, 'vertical'),
])
def test_compact_sheet_header_class_follows_the_photo_shape(
        client, photo_factory, width, height, expected):
    species = create_species(name_fi='valkonarsissi', external_id=1,
                             photo=photo_factory(title='valkonarsissi kukassa',
                                                 width=width, height=height))
    create_planted(species=species, external_id=1)

    content = page(client.get(species_url('planted-species-compact', 1)))

    assert 'class="header {0}"'.format(expected) in content


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['planted-species',
                                      'planted-species-compact'])
def test_reports_render_when_the_image_file_is_missing(client, media_root,
                                                       photo_factory,
                                                       url_name):
    """Was an ``IOError``; see docs/issues/011.

    This is the state of a database restored without ``dev/kasvimuseo media
    fetch``: rows pointing at files that are not there. The stored orientation
    is what makes it renderable -- and a photo measured before its file went
    missing keeps the orientation it was measured with.
    """
    species = create_species(name_fi='valkonarsissi', external_id=1,
                             photo=photo_factory(title='valkonarsissi kukassa',
                                                 width=12, height=8))
    create_planted(species=species, external_id=1)
    os.remove(species.photo.image.path)

    content = page(client.get(species_url(url_name, 1)))

    assert 'valkonarsissi' in content
    assert 'class="header horizontal"' in content


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['planted-species',
                                      'planted-species-compact',
                                      'planted-species-list'])
def test_reports_open_no_image_file(client, full_species,
                                    mobile_thumbnail_size, image_opens,
                                    url_name):
    """The point of docs/issues/011: the header class costs no file access.

    All three reports that put a photo on the page, not just the two that
    picked the header class: the list page asks for a thumbnail URL and the
    other two for a display URL, and the header class was the only one of the
    three that measured the image on every render.

    The first request for a photo is still allowed to touch the original,
    because ``get_<size>_url`` builds photologue's cached copy on demand --
    once per photo and size, ever, and only because the shipped ``PhotoSize``
    rows have ``pre_cache`` off. Warm that, then assert the steady state:
    rendering opens nothing.
    """
    url = (reverse(url_name) if url_name == 'planted-species-list'
           else species_url(url_name, 1))
    client.get(url)
    # The warm-up has to have opened the original, or this page is not putting
    # a photo on the screen at all and the assertion below would pass by
    # testing nothing.
    assert image_opens
    del image_opens[:]

    page(client.get(url))

    assert image_opens == []


@pytest.mark.django_db
def test_reports_build_an_uncached_photo_size(client, display_size,
                                              photo_factory):
    """Issue 028: rendering a report is what builds a missing photo size.

    ``get_display_url()`` calls ``create_size()`` only when the cached file is
    absent, and ``create_size()`` calls ``resize_image()`` only when the
    original is not already the size asked for -- which is where photologue
    asks Pillow for ``Image.ANTIALIAS``, removed in Pillow 10.0.0. There are
    two such calls, one per branch, and the suite reached only the other one:
    the admin photo changelist builds ``admin_thumbnail``, a *cropping* size,
    and the crop branch resizes whatever it is given. The reports use
    ``display``, which does not crop and therefore returns early rather than
    upscale -- and every photo the rest of these tests build is smaller than
    it, so nothing here scaled an image down. This one is twice the size, with
    a cold cache.

    Asserting the cached file rather than the response, because a
    ``PhotoSize`` that is never applied still gives a 200 and a URL.
    """
    from PIL import Image
    from photologue.models import PhotoSizeCache

    photosize = PhotoSizeCache().sizes['display']
    width, height = photosize.size
    photo = photo_factory(width=width * 2, height=height * 2)
    species = create_species(name_fi='valkonarsissi', external_id=1,
                             photo=photo)
    create_planted(species=species, external_id=1)
    assert not photo.size_exists(photosize)

    page(client.get(species_url('planted-species', 1)))

    assert photo.size_exists(photosize)
    assert Image.open(photo.get_display_filename()).size == (width, height)


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
def test_observation_page_has_no_placeholder_image(client):
    """``<img src="dummy.jpg" />`` was hardcoded here; see issues/004."""
    create_planted(name_fi='valkonarsissi', external_id=42)

    content = page(client.get(reverse('planted-observation', args=[42])))

    assert 'dummy.jpg' not in content
    assert '<img' not in content


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


@pytest.mark.django_db
def test_label_editor_issues_the_csrf_cookie_its_save_reads(client):
    """Issue 052: the page renders the token, so the cookie exists.

    ``save`` takes the token out of ``document.cookie``, and rendering the tag
    is what makes ``CsrfViewMiddleware`` set that cookie. Both halves are
    asserted here: without the cookie the save is rejected, and without the
    read from it the JavaScript has nothing to send.
    """
    response = client.get(reverse('planting-label'))

    assert 'csrftoken' in response.cookies
    assert 'csrfmiddlewaretoken' in page(response)
    assert 'document.cookie.match(' in page(response)


@pytest.mark.django_db
def test_label_editor_names_the_photo_buttons(client):
    """The chevrons are glyphs, so the attributes are their only name (037)."""
    content = page(client.get(reverse('planting-label')))

    for direction in ['Edellinen', 'Seuraava']:
        name = '{0} kuva t\xe4lle kyltille'.format(direction)
        assert 'title="{0}"'.format(name) in content
        assert 'aria-label="{0}"'.format(name) in content


@pytest.mark.django_db
def test_label_editor_says_what_the_photo_choice_applies_to(client):
    """The label's own photo, kept once saved -- what issue 039 implemented."""
    content = page(client.get(reverse('planting-label')))

    assert 'vain t\xe4m\xe4n kyltin kuvan, eiv\xe4t lajin kuvaa' in content
    assert 'Valinta s\xe4ilyy, kun napsautat \u201cSave changes\u201d' in content
    # A photo choice enables the save button; without this the sentence above
    # would not be reachable.
    assert "'species.photo_pk': function" in content


# A species external id that does not exist


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['planted-species',
                                      'planted-species-compact'])
def test_unknown_external_id_404s(client, url_name):
    """Was an empty 200 page; see docs/issues/007."""
    create_planted(name_fi='valkonarsissi', external_id=1)

    response = client.get(species_url(url_name, 999999))

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['planted-species',
                                      'planted-species-compact'])
def test_partly_unknown_external_id_still_renders_what_matched(client,
                                                               url_name):
    """Only the wholly empty case 404s; see docs/issues/007."""
    create_planted(name_fi='valkonarsissi', external_id=1)

    content = page(client.get(
        reverse(url_name, kwargs={'species_external_ids': '1,999999'})))

    assert 'valkonarsissi' in content


# The tablet viewport and the print buttons; see docs/issues/045
#
# What these assert is the markup, which is all the server can be asked about:
# whether the tag has the effect it is there for, and whether the button is
# absent from the paper, are questions for a browser and a printer -- see issue
# 017 for why neither is asked here.


VIEWPORT_TAG = ('<meta name="viewport" '
                'content="width=device-width, initial-scale=1">')


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,external_id', [
    ('planted-species-list', None),
    ('planting-label', None),
    ('planted-species', 1),
    ('planted-species-compact', 1),
])
def test_report_pages_lay_out_at_the_device_width(client, url_name,
                                                 external_id):
    create_planted(name_fi='ahdekaunokki', external_id=1)

    url = (species_url(url_name, external_id) if external_id
           else reverse(url_name))

    assert VIEWPORT_TAG in page(client.get(url))


def test_the_public_base_template_lays_out_at_the_device_width():
    """``base.html`` is what photologue's pages extend, and had no ``<head>``."""
    assert VIEWPORT_TAG in render_to_string('base.html')


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,external_id,caption', [
    ('planting-label', None, 'Print'),
    ('planted-species', 1, 'Tulosta'),
    ('planted-species-compact', 1, 'Tulosta'),
])
def test_printable_pages_offer_a_print_button(client, url_name, external_id,
                                              caption):
    """iPadOS Safari's own print command is in the Share menu, not on a bar."""
    create_planted(name_fi='ahdekaunokki', external_id=1)

    url = (species_url(url_name, external_id) if external_id
           else reverse(url_name))
    content = page(client.get(url))

    assert 'onclick="window.print()"' in content
    assert '>{0}</button>'.format(caption) in content


@pytest.mark.django_db
def test_the_label_print_toggle_needs_no_hover(client):
    """It was revealed by ``opacity: 0`` plus hover, which a touch screen lacks.

    The toggle is drawn by default now, and only a device that *has* a hover
    takes it away again. ``.remove`` is in the ``@media print`` hide list, so
    nothing but that list keeps it off the paper.
    """
    content = page(client.get(reverse('planting-label')))

    hide_list = re.search(r'@media print \{\s*([^}]*)\}', content)
    assert hide_list, 'the page has no @media print block at all'
    assert '.remove' in hide_list.group(1)
    # The default -- what a touch screen gets -- is visible.
    default = re.search(r'\n        \.remove \{([^}]*)\}', content)
    assert default, 'the page has no unconditional ``.remove`` rule'
    assert 'opacity: 0.5;' in default.group(1)
    # Hiding it again is scoped to devices that can hover, and the script that
    # dims it back in is scoped to the same query.
    hover_only = re.search(r'@media \(hover: hover\) \{(.*?)\n        \}\n',
                           content, re.DOTALL)
    assert hover_only, 'nothing is scoped to ``@media (hover: hover)``'
    assert 'opacity: 0;' in hover_only.group(1)
    assert 'body.pointer-active .remove' in hover_only.group(1)
    assert "matchMedia('(hover: hover)')" in content
    assert "classList.add('pointer-active')" in content


@pytest.mark.django_db
def test_a_label_left_out_of_the_run_is_dimmed_by_its_contents(client):
    """``opacity`` on the ``li`` would take the print toggle down with it.

    It makes a compositing group, so the toggle inside renders against the
    dimming however opaque its own rule says it is -- 89 levels paler on an
    unchecked label, while ``getComputedStyle`` reports the same 0.5 for both.
    No assertion here can see that; what it can do is pin the shape of the rule
    that avoids it.
    """
    content = page(client.get(reverse('planting-label')))

    dimmed = re.search(r'li\.hidden > \*:not\(\.remove\) \{([^}]*)\}', content)
    assert dimmed, 'nothing dims a label around its print toggle'
    assert 'opacity: 0.3;' in dimmed.group(1)
    # The box itself must not be dimmed, only what is in it besides the toggle.
    box = re.search(r'\n        li\.hidden \{([^}]*)\}', content)
    assert box, 'the ``li.hidden`` rule is gone'
    assert 'opacity' not in box.group(1)
