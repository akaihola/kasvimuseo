# -*- coding: utf-8 -*-
"""Tests for the rendered admin changelist.

The project ships its own ``admin/change_list.html`` and a fork of Django's
``admin_list`` in ``kasvimuseo.templatetags.kasvimuseo_admin_list`` whose only
purpose is to put ``fieldname_<name>`` classes on every header and cell
(Django ticket #11195), so ``kasvimuseo.admin.css`` can target columns. These
tests assert that markup, plus the sorting, filtering, ordering and fieldset
behaviour the ModelAdmins declare.
"""

from __future__ import unicode_literals

import re

import pytest
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from kasvimuseo import admin
from kasvimuseo.models import Care, Observation, Planting, Species
from kasvimuseo.templatetags.kasvimuseo_admin_list import identifier_for_field
from kasvimuseo.tests import factories


CELL_RE = re.compile(r'<(th|td)\b[^>]*?class="([^"]*)"', re.S)
ROW_RE = re.compile(r'<tr class="grp-row.*?</tr>', re.S)


def search(pattern, text, flags=re.S):
    """``re.search`` that fails the test instead of returning ``None``."""
    match = re.search(pattern, text, flags)
    assert match is not None, pattern
    return match


def thead(html):
    return search(r'<thead>.*?</thead>', html).group(0)


def get(admin_client, model, view='changelist', query=''):
    url = reverse('admin:kasvimuseo_{0}_{1}'.format(model._meta.module_name,
                                                    view))
    response = admin_client.get(url + query)
    assert response.status_code == 200
    return response.content.decode('utf-8')


def cell_classes(html):
    """``{'th'|'td': set of class names}`` for every cell in ``html``."""
    found = {'th': set(), 'td': set()}
    for tag, classes in CELL_RE.findall(html):
        found[tag].update(classes.split())
    return found


def column_values(html, identifier):
    """The text of column ``identifier``, one entry per row.

    The first column is wrapped in the change link, so tags are stripped.
    """
    pattern = re.compile(
        r'<t[dh][^>]*class="[^"]*fieldname_{0}[ "][^>]*>(.*?)</t[dh]>'.format(
            identifier), re.S)
    return [re.sub(r'<[^>]+>', '', pattern.search(row).group(1)).strip()
            for row in ROW_RE.findall(html)]


# ---------------------------------------------------------------------------
# 1. field-name classes
# ---------------------------------------------------------------------------

@pytest.fixture
def species(db):
    return factories.create_species(name_fi='valkonarsissi', external_id=11)


@pytest.mark.parametrize('identifier', [
    'edit',           # a plain function in list_display
    'external_id',    # a real model field
    'name_fi',
    'genus',
    'type',
    'photo_image',    # a ModelAdmin attribute
])
def test_species_changelist_field_classes(admin_client, species, identifier):
    """Every column carries its ``fieldname_`` class in header and body."""
    html = get(admin_client, Species)
    classes = cell_classes(html)

    assert 'fieldname_{0}'.format(identifier) in classes['th'] | classes['td']
    # and the class reaches the data cells, not just the header
    assert len(column_values(html, identifier)) == 1


@pytest.mark.parametrize('identifier', [
    'edit',
    'observation_external_id',   # a model attribute (a method on Planting)
    'bed',
    'coordinates',               # a ModelAdmin method
])
def test_planting_changelist_field_classes(admin_client, identifier):
    factories.create_planted()
    html = get(admin_client, Planting)
    classes = cell_classes(html)

    assert 'fieldname_{0}'.format(identifier) in classes['th'] | classes['td']
    assert len(column_values(html, identifier)) == 1


def test_identifier_for_field_branches():
    """The five lookup branches of the ticket #11195 fork."""
    assert identifier_for_field('name_fi', Species) == 'name_fi'
    assert identifier_for_field('__unicode__', Species) == 'species'
    assert identifier_for_field(str('__str__'), Species) == str('species')
    assert identifier_for_field(lambda obj: obj, Species) == '__lambda__'
    assert identifier_for_field(admin.edit, Species) == 'edit'
    # a ModelAdmin attribute...
    assert identifier_for_field(
        'photo_image', Species, model_admin=admin.SpeciesAdmin) \
        == 'photo_image'
    # ...and a model attribute
    assert identifier_for_field('observation_external_id', Planting) \
        == 'observation_external_id'
    with pytest.raises(AttributeError):
        identifier_for_field('nonexistent', Species)


# ---------------------------------------------------------------------------
# 2. sorting and the action checkbox column
# ---------------------------------------------------------------------------

def sortable_column_index(model_admin, field_name):
    """The ``?o=`` index of ``field_name``.

    Django prepends ``action_checkbox`` to ``list_display`` whenever the
    ModelAdmin has actions, and ``ORDER_VAR`` counts from that list.
    """
    return list(model_admin.list_display).index(field_name) + 1


def test_action_checkbox_column(admin_client, species):
    html = get(admin_client, Species)
    classes = cell_classes(html)

    # the header gets the special class instead of a fieldname_ one...
    assert 'action-checkbox-column' in classes['th']
    # ...while the body cell gets both
    assert 'action-checkbox' in classes['td']
    assert 'fieldname_action_checkbox' in classes['td']


def test_changelist_sorting_marks_the_sorted_header(admin_client, species):
    index = sortable_column_index(admin.SpeciesAdmin, 'name_fi')
    html = get(admin_client, Species, query='?o={0}'.format(index))

    header = search(r'<th[^>]*class="([^"]*fieldname_name_fi[^"]*)"(.*?)</th>',
                    thead(html))
    assert set(header.group(1).split()) == set(
        ['sortable', 'fieldname_name_fi', 'sorted', 'ascending'])
    # the toggle flips to descending and a remove link appears
    assert 'grp-toggle grp-ascending' in header.group(2)
    assert 'o=-{0}'.format(index) in header.group(2)   # url_toggle
    assert 'grp-sortremove' in header.group(2)

    descending = thead(
        get(admin_client, Species, query='?o=-{0}'.format(index)))
    classes = search(r'<th[^>]*class="([^"]*fieldname_name_fi[^"]*)"',
                     descending).group(1)
    assert 'descending' in classes.split()


def test_changelist_sorting_orders_the_rows(admin_client, db):
    for name in ['kissankello', 'akileija', 'valkonarsissi']:
        factories.create_species(name_fi=name)
    index = sortable_column_index(admin.SpeciesAdmin, 'name_fi')

    html = get(admin_client, Species, query='?o={0}'.format(index))

    assert column_values(html, 'name_fi') == [
        'akileija', 'kissankello', 'valkonarsissi']


# ---------------------------------------------------------------------------
# 3. list_filter -- the standing "FIXME: filtering doesn't work" comments
# ---------------------------------------------------------------------------

def test_species_list_filter(admin_client, db):
    """``SpeciesAdmin.list_filter = ("type",)`` -- carries a FIXME comment.

    Filtering *does* work: both the bare ``?type=`` lookup and the
    ``?type__exact=`` one the rendered filter link uses narrow the rows.
    """
    factories.create_species(name_fi='perenna', type=2)
    factories.create_species(name_fi='yrtti', type=3)

    for query in ['?type=2', '?type__exact=2']:
        html = get(admin_client, Species, query=query)
        assert column_values(html, 'name_fi') == ['perenna'], query

    # and the filter links the sidebar renders point at that lookup
    assert 'type__exact=2' in get(admin_client, Species)


def test_observation_list_filter(admin_client, db):
    """``ObservationAdmin.list_filter`` -- also carries a FIXME comment."""
    wanted = factories.create_observation(
        origin=factories.create_location(name='Talo'), external_id=11)
    factories.create_observation(
        origin=factories.create_location(name='Torppa'), external_id=22)

    html = get(admin_client, Observation,
               query='?origin__id__exact={0}'.format(wanted.origin_id))

    assert column_values(html, 'external_id') == ['11']


def test_care_list_filter(admin_client, db):
    """``CareAdmin.list_filter`` -- the third FIXME comment."""
    wanted = factories.create_planted(bed=factories.create_bed(name='1'))
    factories.create_care(wanted, description='harvennus')
    factories.create_care(
        factories.create_planted(bed=factories.create_bed(name='2')),
        description='suojaus')

    html = get(admin_client, Care,
               query='?planting__bed__id__exact={0}'.format(wanted.bed_id))

    assert column_values(html, 'description') == ['harvennus']


def test_planting_list_filter(admin_client, db):
    bed = factories.create_bed(name='1')
    factories.create_planted(bed=bed, external_id=11)
    factories.create_planted(bed=factories.create_bed(name='2'),
                             external_id=22)

    html = get(admin_client, Planting,
               query='?bed__id__exact={0}'.format(bed.pk))

    assert column_values(html, 'observation_external_id') == ['11']


# ---------------------------------------------------------------------------
# 4. PlantingAdmin.ordering
# ---------------------------------------------------------------------------

def test_planting_changelist_uses_the_declared_ordering(admin_client, db):
    """``ordering = 'observation__external_id',`` beats insertion order."""
    for external_id in [30, 10, 20]:
        factories.create_planted(external_id=external_id)

    html = get(admin_client, Planting)

    assert column_values(html, 'observation_external_id') == ['10', '20', '30']


# ---------------------------------------------------------------------------
# 5. fieldsets on the add pages
# ---------------------------------------------------------------------------

def test_observation_add_page_fieldsets(admin_client, db):
    html = get(admin_client, Observation, view='add')
    fieldsets = re.findall(
        r'<fieldset class="grp-module ([^"]*)">'
        r'(?:<h2[^>]*>([^<]*)</h2>)?', html)

    assert fieldsets[:2] == [('fieldset_column', ugettext('Basic information')),
                             ('', ugettext('Extra information'))]
    # the declared fields of the first group are the ones rendered in it
    first = search(r'<fieldset class="grp-module fieldset_column">.*?'
                   r'</fieldset>', html).group(0)
    for field in ['external_id', 'origin', 'species', 'variation', 'date']:
        assert 'name="{0}"'.format(field) in first
    assert 'name="nickname"' not in first


def test_species_add_page_has_one_unnamed_fieldset(admin_client, db):
    html = get(admin_client, Species, view='add')
    fieldsets = re.findall(r'<fieldset class="grp-module ([^"]*)">'
                           r'(<h2)?', html)

    # a single ``(None, {...})`` group: no classes, no legend
    assert fieldsets[0] == ('', '')
    for field in admin.SpeciesAdmin.fieldsets[0][1]['fields']:
        assert 'name="{0}"'.format(field) in html


# ---------------------------------------------------------------------------
# 6. the Media CSS hook
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('model', [Species, Observation, Planting],
                         ids=lambda model: model.__name__)
def test_changelist_links_the_admin_stylesheet(admin_client, db, model):
    assert admin.ADMIN_CSS_PATH in get(admin_client, model)


# ---------------------------------------------------------------------------
# 7. PhotoAdmin swaps title for image_filename
# ---------------------------------------------------------------------------

def get_photos(admin_client, query=''):
    """The photo changelist: photologue's model, so ``get`` cannot name it."""
    url = reverse('admin:photologue_photo_changelist')
    response = admin_client.get(url + query)
    assert response.status_code == 200
    return response.content.decode('utf-8')


def test_photo_changelist_shows_the_file_name(admin_client, photo_factory):
    photo = photo_factory(title='valkonarsissi kukassa')
    html = get_photos(admin_client)

    assert 'fieldname_title' not in html
    assert column_values(html, 'image_filename') == [
        photo.image.name.split('/')[-1]]


def test_photo_changelist_file_name_header_is_a_sort_link(admin_client,
                                                          photo_factory):
    """``image_filename.admin_order_field`` -- issue 043."""
    photo_factory(title='valkonarsissi kukassa')
    index = sortable_column_index(admin.PhotoAdmin, 'image_filename')

    header = search(
        r'<th[^>]*class="([^"]*fieldname_image_filename[^"]*)"(.*?)</th>',
        thead(get_photos(admin_client)))

    assert 'sortable' in header.group(1).split()
    assert 'o={0}'.format(index) in header.group(2)


def test_photo_changelist_sorting_orders_the_rows(admin_client, photo_factory):
    """``?o=`` on that column really orders by file name.

    All lowercase on purpose: the sort is the database's, and the development
    cluster's ``C`` collation and production's ``en_US.UTF-8`` one disagree
    about where an upper-case initial goes. See the issue.
    """
    for title in ['kissankello', 'akileija', 'valkonarsissi']:
        photo_factory(title=title)
    index = sortable_column_index(admin.PhotoAdmin, 'image_filename')

    ascending = column_values(
        get_photos(admin_client, '?o={0}'.format(index)), 'image_filename')

    assert ascending == ['akileija.jpg', 'kissankello.jpg',
                         'valkonarsissi.jpg']
    assert column_values(
        get_photos(admin_client, '?o=-{0}'.format(index)),
        'image_filename') == list(reversed(ascending))
