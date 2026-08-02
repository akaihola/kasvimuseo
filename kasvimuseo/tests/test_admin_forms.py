# -*- coding: utf-8 -*-
"""Write paths through the admin: add, change, delete, inlines and actions.

Everything here goes through ``admin_client.post()`` -- the rest of the admin
suite only ever issues GETs, so form handling, inline formsets and validation
were completely uncovered.

Django 1.5 refuses to process an admin POST without the management form of
every inline, so :func:`management` builds those keys and :func:`post_add`
adds an empty one for each inline the ``ModelAdmin`` declares. The prefixes
were read off the rendered add pages, not guessed.
"""

from __future__ import unicode_literals

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

from kasvimuseo import admin  # noqa: F401  (registers the ModelAdmins)
from kasvimuseo.models import (
    Bed, Care, Contact, Location, Observation, Planting, Plot, Species)
from kasvimuseo.tests import factories
from kasvimuseo.tests.conftest import jpeg_bytes
from photologue.models import Photo


INLINE_PREFIXES = {
    Species: ['observation_set'],
    Location: ['locationcontact_set', 'observation_set'],
    Planting: ['care_set'],
    Plot: ['bed_set'],
    Photo: ['species_set'],
}


def admin_url(model, page, *args):
    return reverse('admin:{0}_{1}_{2}'.format(model._meta.app_label,
                                              model._meta.module_name,
                                              page),
                   args=args)


def management(prefix, total=0, initial=0):
    """The three keys Django 1.5 requires from every inline formset."""
    return {'{0}-TOTAL_FORMS'.format(prefix): '{0}'.format(total),
            '{0}-INITIAL_FORMS'.format(prefix): '{0}'.format(initial),
            '{0}-MAX_NUM_FORMS'.format(prefix): ''}


def payload(model, data, extra=None):
    result = {}
    for prefix in INLINE_PREFIXES.get(model, []):
        result.update(management(prefix))
    result.update(data)
    result.update(extra or {})
    return result


def post_add(admin_client, model, data, extra=None):
    return admin_client.post(admin_url(model, 'add'),
                             payload(model, data, extra))


def form_errors(response):
    return response.context['adminform'].form.errors


# -- add ---------------------------------------------------------------------

def _add_species():
    return (Species,
            {'name_fi': 'kevätesikko', 'genus': 'Primula',
             'species': 'veris', 'type': '2'},
            {'name_fi': 'kevätesikko', 'genus': 'Primula', 'type': 2})


def _add_location():
    return (Location,
            {'name': 'Mäkelä', 'village': 'Yläne'},
            {'name': 'Mäkelä', 'village': 'Yläne'})


def _add_contact():
    return (Contact,
            {'last_name': 'Virtanen', 'first_name': 'Maija'},
            {'last_name': 'Virtanen', 'first_name': 'Maija'})


def _add_plot():
    return Plot, {'name': 'Etupiha'}, {'name': 'Etupiha'}


def _add_bed():
    plot = factories.create_plot()
    return (Bed,
            {'name': '7', 'plot': '{0}'.format(plot.pk), 'public': 'on'},
            {'name': '7', 'plot': plot, 'public': True})


def _add_observation():
    species = factories.create_species()
    origin = factories.create_location()
    return (Observation,
            {'species': '{0}'.format(species.pk),
             'origin': '{0}'.format(origin.pk),
             'date': '2020-01-01',
             'nickname': 'mummon narsissi'},
            {'species': species, 'origin': origin,
             'nickname': 'mummon narsissi'})


def _add_planting():
    observation = factories.create_observation()
    bed = factories.create_bed()
    return (Planting,
            {'observation': '{0}'.format(observation.pk),
             'bed': '{0}'.format(bed.pk),
             'planting_date': '2020-05-01', 'count': '4',
             'distance_left': '10', 'distance_front': '20',
             'width': '30', 'depth': '40'},
            {'observation': observation, 'bed': bed, 'count': 4,
             'width': 30})


def _add_care():
    planting = factories.create_planting()
    return (Care,
            {'planting': '{0}'.format(planting.pk), 'date': '2020-06-01',
             'description': 'harvennus', 'count': '2'},
            {'planting': planting, 'description': 'harvennus', 'count': 2})


ADD_CASES = [('species', _add_species),
             ('location', _add_location),
             ('contact', _add_contact),
             ('plot', _add_plot),
             ('bed', _add_bed),
             ('observation', _add_observation),
             ('planting', _add_planting),
             ('care', _add_care)]


@pytest.mark.django_db
@pytest.mark.parametrize('build', [case[1] for case in ADD_CASES],
                         ids=[case[0] for case in ADD_CASES])
def test_admin_add_creates_object(admin_client, build):
    model, data, expected = build()
    before = model.objects.count()

    response = post_add(admin_client, model, data)

    assert response.status_code == 302
    assert model.objects.count() == before + 1
    assert model.objects.filter(**expected).count() == 1


# -- change ------------------------------------------------------------------

@pytest.mark.django_db
def test_admin_change_species_persists_field(admin_client):
    species = factories.create_species(name_fi='valkonarsissi')

    response = admin_client.post(
        admin_url(Species, 'change', species.pk),
        payload(Species, {'name_fi': 'keltanarsissi', 'genus': 'Narcissus',
                          'species': 'pseudonarcissus', 'type': '2'}))

    assert response.status_code == 302
    species = Species.objects.get(pk=species.pk)
    assert species.name_fi == 'keltanarsissi'
    assert species.species == 'pseudonarcissus'


@pytest.mark.django_db
def test_admin_change_planting_persists_field(admin_client):
    planting = factories.create_planting(count=3)

    response = admin_client.post(
        admin_url(Planting, 'change', planting.pk),
        payload(Planting,
                {'observation': '{0}'.format(planting.observation_id),
                 'bed': '{0}'.format(planting.bed_id),
                 'planting_date': '2020-05-01', 'count': '9',
                 'distance_left': '15', 'distance_front': '15',
                 'width': '15', 'depth': '15'}))

    assert response.status_code == 302
    assert Planting.objects.get(pk=planting.pk).count == 9


# -- validation --------------------------------------------------------------

@pytest.mark.django_db
def test_admin_add_species_without_name_redisplays_form(admin_client):
    response = post_add(admin_client, Species,
                        {'genus': 'Primula', 'species': 'veris', 'type': '2'})

    assert response.status_code == 200
    assert 'name_fi' in form_errors(response)
    assert not Species.objects.exists()


@pytest.mark.django_db
def test_admin_add_planting_without_count_redisplays_form(admin_client):
    observation = factories.create_observation()
    bed = factories.create_bed()

    response = post_add(admin_client, Planting,
                        {'observation': '{0}'.format(observation.pk),
                         'bed': '{0}'.format(bed.pk),
                         'planting_date': '2020-05-01',
                         'distance_left': '15', 'distance_front': '15',
                         'width': '15', 'depth': '15'})

    assert response.status_code == 200
    assert 'count' in form_errors(response)
    assert not Planting.objects.exists()


# -- inlines carrying data ---------------------------------------------------

@pytest.mark.django_db
def test_admin_add_planting_with_care_inline(admin_client):
    observation = factories.create_observation()
    bed = factories.create_bed()

    response = post_add(
        admin_client, Planting,
        {'observation': '{0}'.format(observation.pk),
         'bed': '{0}'.format(bed.pk),
         'planting_date': '2020-05-01', 'count': '4',
         'distance_left': '15', 'distance_front': '15',
         'width': '15', 'depth': '15'},
        extra=dict(management('care_set', total=1),
                   **{'care_set-0-date': '2020-06-01',
                      'care_set-0-description': 'harvennus',
                      'care_set-0-count': '2'}))

    assert response.status_code == 302
    planting = Planting.objects.get()
    care = Care.objects.get()
    assert care.planting == planting
    assert care.description == 'harvennus'
    assert care.count == 2


@pytest.mark.django_db
def test_admin_add_species_with_observation_inline(admin_client):
    origin = factories.create_location()

    response = post_add(
        admin_client, Species,
        {'name_fi': 'kevätesikko', 'genus': 'Primula', 'species': 'veris',
         'type': '2'},
        extra=dict(management('observation_set', total=1),
                   **{'observation_set-0-origin': '{0}'.format(origin.pk),
                      'observation_set-0-date': '2020-01-01',
                      'observation_set-0-nickname': 'esikko'}))

    assert response.status_code == 302
    species = Species.objects.get()
    observation = Observation.objects.get()
    assert observation.species == species
    assert observation.origin == origin
    assert observation.nickname == 'esikko'


@pytest.mark.django_db
def test_admin_invalid_inline_row_blocks_the_whole_save(admin_client):
    """A broken Care row keeps the otherwise valid Planting from being saved."""
    observation = factories.create_observation()
    bed = factories.create_bed()

    response = post_add(
        admin_client, Planting,
        {'observation': '{0}'.format(observation.pk),
         'bed': '{0}'.format(bed.pk),
         'planting_date': '2020-05-01', 'count': '4',
         'distance_left': '15', 'distance_front': '15',
         'width': '15', 'depth': '15'},
        extra=dict(management('care_set', total=1),
                   **{'care_set-0-date': '2020-06-01',
                      'care_set-0-description': 'harvennus'}))  # no count

    assert response.status_code == 200
    formset = response.context['inline_admin_formsets'][0].formset
    assert 'count' in formset.errors[0]
    assert not Planting.objects.exists()
    assert not Care.objects.exists()


# -- delete ------------------------------------------------------------------

DELETE_CASES = [
    ('species', lambda: factories.create_species()),
    ('location', lambda: factories.create_location()),
    ('plot', lambda: factories.create_plot()),
    ('planting', lambda: factories.create_planting()),
]


@pytest.mark.django_db
@pytest.mark.parametrize('build', [case[1] for case in DELETE_CASES],
                         ids=[case[0] for case in DELETE_CASES])
def test_admin_delete(admin_client, build):
    obj = build()
    model = type(obj)
    url = admin_url(model, 'delete', obj.pk)

    assert admin_client.get(url).status_code == 200

    response = admin_client.post(url, {'post': 'yes'})

    assert response.status_code == 302
    assert not model.objects.filter(pk=obj.pk).exists()


# -- changelist action -------------------------------------------------------

@pytest.mark.django_db
def test_planted_species_report_action_from_changelist(admin_client):
    """``admin.py`` carries a ``# FIXME: action selection doesn't work``.

    Driven through the changelist the action does work: the POST comes back as
    a redirect to the species-sheet URL built from the selected external ids.
    """
    first = factories.create_species(name_fi='keltanarsissi', external_id=22)
    second = factories.create_species(name_fi='valkonarsissi', external_id=11)

    response = admin_client.post(
        admin_url(Species, 'changelist'),
        {'action': 'planted_species_report',
         'index': '0',
         '_selected_action': ['{0}'.format(first.pk),
                              '{0}'.format(second.pk)]})

    assert response.status_code == 302
    # The changelist orders by ``name_fi``, so keltanarsissi (22) comes first.
    assert response['Location'].endswith(
        reverse('planted-species',
                kwargs={'species_external_ids': '22,11'}))


@pytest.mark.django_db
def test_planted_species_report_action_without_selection(admin_client):
    """With nothing selected the changelist is redisplayed, not redirected."""
    factories.create_species(external_id=11)

    response = admin_client.post(admin_url(Species, 'changelist'),
                                 {'action': 'planted_species_report',
                                  'index': '0'})

    assert response.status_code == 200


# -- photo upload ------------------------------------------------------------

@pytest.mark.django_db
def test_photo_admin_upload_derives_title_and_connects_species(admin_client,
                                                               media_root):
    """A blank title makes ``PhotoForm.clean`` name the photo after the file.

    Saving it then fires ``autoconnect_photo_to_species``, which attaches the
    photo to the species named by the first word of the derived title.
    """
    species = factories.create_species(name_fi='valkonarsissi')
    upload = SimpleUploadedFile('valkonarsissi kukassa.jpg', jpeg_bytes(),
                                content_type=str('image/jpeg'))

    response = post_add(admin_client, Photo,
                        {'title': '', 'slug': '',
                         # ``date_added`` is a DateTimeField, and the admin
                         # splits those into two widgets.
                         'date_added_0': '2020-05-01',
                         'date_added_1': '12:00:00',
                         'image': upload,
                         'is_public': 'on'})

    assert response.status_code == 302, form_errors(response)
    photo = Photo.objects.get()
    assert photo.title == 'valkonarsissi kukassa'
    assert photo.slug == 'valkonarsissi-kukassa'
    assert Species.objects.get(pk=species.pk).photo == photo


# -- the species photo (issue 037) -------------------------------------------

@pytest.mark.django_db
def test_admin_change_species_detaches_the_photo(admin_client, photo_factory):
    """Blank means "no photo", and the file survives it.

    Before the ``photo`` field was on the form, the only way to take a photo
    off a species was to delete the ``Photo`` row, which deletes the image for
    every other use of it.
    """
    species = factories.create_species(name_fi='valkonarsissi')
    species.photo = photo_factory(title='valkonarsissi kukassa')
    species.save()

    response = admin_client.post(
        admin_url(Species, 'change', species.pk),
        payload(Species, {'name_fi': 'valkonarsissi', 'genus': 'Narcissus',
                          'species': 'poeticus', 'type': '2', 'photo': ''}))

    assert response.status_code == 302, form_errors(response)
    assert Species.objects.get(pk=species.pk).photo is None
    assert Photo.objects.count() == 1


@pytest.mark.django_db
def test_admin_change_species_selects_another_photo(admin_client,
                                                    photo_factory):
    species = factories.create_species(name_fi='valkonarsissi')
    species.photo = photo_factory(title='valkonarsissi kukassa')
    species.save()
    other = photo_factory(title='valkonarsissi lehdet')

    response = admin_client.post(
        admin_url(Species, 'change', species.pk),
        payload(Species, {'name_fi': 'valkonarsissi', 'genus': 'Narcissus',
                          'species': 'poeticus', 'type': '2',
                          'photo': '{0}'.format(other.pk)}))

    assert response.status_code == 302, form_errors(response)
    assert Species.objects.get(pk=species.pk).photo == other


@pytest.mark.django_db
def test_admin_change_species_refuses_another_species_photo(admin_client,
                                                            photo_factory):
    """The choices are this species' photos, and the form enforces it."""
    species = factories.create_species(name_fi='valkonarsissi')
    stranger = photo_factory(title='keltanarsissi')

    response = admin_client.post(
        admin_url(Species, 'change', species.pk),
        payload(Species, {'name_fi': 'valkonarsissi', 'genus': 'Narcissus',
                          'species': 'poeticus', 'type': '2',
                          'photo': '{0}'.format(stranger.pk)}))

    assert response.status_code == 200
    assert 'photo' in form_errors(response)
    assert Species.objects.get(pk=species.pk).photo is None
