# pylint: disable=E1101
#         Instance has no 'X' method/attribute
# pylint: disable=W0142
#         Used * or ** magic
import json
from collections import OrderedDict
from functools import wraps
from itertools import groupby
from operator import attrgetter

from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View, ListView
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.detail import DetailView

from kasvimuseo.models import Bed, Observation, Species, Label, Planting
from kasvimuseo.photos import (get_photo_pks_and_urls_by_species,
                               get_species_photo_info)


class PlantedSpeciesList(ListView):
    template_name = 'kasvimuseo/reports/planted-species-list.html'
    model = Species

    def get_queryset(self):
        """Returns public planted species ordered by Finnish name

        The :meth:`get_queryset` method is used instead of the ``queryset``
        attribute, because
        :meth:`kasvimuseo.models.SpeciesManager.public_planted` is not lazy and
        needs to be evaluated every time.

        """
        return (self.model.objects
                .public_planted()
                .distinct()
                .order_by('name_fi'))


class PlantedSpeciesLabels(TemplateView):
    template_name = 'kasvimuseo/reports/planting-labels.html'


def staff_only_api(view):
    """Refuse a non-staff request with 403, rather than a page it cannot use.

    ``staff_member_required`` answers with the admin's login form and a status
    of 200, which is right for a page and wrong for the endpoint the editor
    calls with axios: HTML behind a 200 is the silent success this whole issue
    is about (issue 052). The editor page itself is gated the admin way, so a
    browser only arrives here unauthenticated when its session has expired
    underneath it -- and then the editor says so, because a 403 is a rejection
    axios reports.
    """
    @wraps(view)
    def _checkstaff(request, *args, **kwargs):
        if not (request.user.is_active and request.user.is_staff):
            return HttpResponseForbidden(
                'The planting labels can only be read and written by a staff'
                ' member. Log in to the admin and reload the editor.',
                content_type='text/plain')
        return view(request, *args, **kwargs)
    return _checkstaff


class PlantedSpeciesLabelsApi(View):
    def get_queryset(self):
        """Returns public planted species ordered by Finnish name

        The :meth:`get_queryset` method is used instead of the ``queryset``
        attribute, because
        :meth:`kasvimuseo.models.SpeciesManager.public_planted` is not lazy and
        needs to be evaluated every time.

        """
        return (Observation.objects
                .public_planted()
                .distinct()
                .order_by('species__name_fi'))

    @staticmethod
    def get_species_data(species, observation_set, label,
                         photo_pks_and_urls_by_title):
        """Build the JSON entry for one label.

        ``label`` is the saved :class:`~kasvimuseo.models.Label` for this
        species, or ``None`` for a species that has none yet. The label is what
        carries the photo choice and the visibility, so both are read from it
        and only fall back to the species defaults when there is no label
        (issue 039).

        ``observation_set`` is ordered by museum number here rather than by
        each caller, so that both ways into this method -- a species whose
        label already exists and one that has none yet -- print the same order
        (issue 053). A museum number that is not set sorts first, which is
        what ``kasvimuseo_model_tags.external_ids`` and the editor's own
        ``insort`` do with it.
        """
        observations = sorted(observation_set, key=attrgetter('external_id'))
        photo_pk, photo_alternatives = get_species_photo_info(
            species, photo_pks_and_urls_by_title,
            photo=label.photo if label else None)
        return {
            'id': species.pk,
            'name_fi': species.name_fi,
            'photo_pk': photo_pk,
            'all_photos': photo_alternatives,
            'external_ids': [observation.external_id
                             for observation in observations],
            'genus': species.genus,
            'species': species.species,
            'group': species.group,
            'subspecies': species.subspecies,
            'nicknames': [observation.nickname
                          for observation in observations],
            'visible': label.visible if label else True}

    def get_labels_data(self):
        # optimize the observations query
        queryset = (self.get_queryset()
                    .only('external_id',
                          'species__id', 'species__name_fi',
                          'species__photo__image',
                          'species__genus', 'species__species',
                          'species__group', 'species__subspecies')
                    .select_related('species__photo'))
        all_photos = get_photo_pks_and_urls_by_species()
        # noinspection PyUnresolvedReferences
        observations_by_species = OrderedDict([
            # ``list()`` because ``groupby`` invalidates the group the moment
            # the next one is asked for; the ordering is
            # ``get_species_data``'s (issue 053).
            (species, list(observation_set))
            for species, observation_set
            in groupby(queryset, attrgetter('species'))])
        labels = (Label.objects
                  .select_related('species', 'photo')
                  .order_by('species__name_fi'))
        labels_by_species = groupby(labels, attrgetter('species'))
        label_infos = [
            self.get_species_data(species,
                                  [planting.observation
                                   for planting in label.planting_set.all()],
                                  label,
                                  all_photos)
            for species, labels in labels_by_species
            for label in labels]
        label_species_pks = {label['id'] for label in label_infos}
        for species, observation_set in observations_by_species.items():
            if species.pk not in label_species_pks:
                label_infos.append(
                    self.get_species_data(species,
                                          observation_set,
                                          None,
                                          all_photos))
        vue_data = {'object_list': label_infos}
        return vue_data

    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        vue_data = self.get_labels_data()
        return HttpResponse(json.dumps(vue_data),
                            content_type='application/json',
                            **kwargs)

    # noinspection PyUnusedLocal
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Replace every label with the submitted set and re-link the plantings.

        The whole replacement is one transaction: the old labels are deleted
        first, so a failure part way through used to leave the table empty
        (issue 010).

        ``atomic`` rather than ``commit_on_success``, which is what issue 010
        wrote here: Django 1.6 turned database-level autocommit on and
        deprecated the whole managed-mode API this decorator came from
        (upgrade plan Stage 3). The old name still works on 1.6 and 1.7 and is
        deleted in 1.8, so this is the same transaction under the name that
        survives the rest of the plan -- and it is the only place in this
        repository that asked for one.

        The labels are created one at a time and mapped to the item that asked
        for each as they are created. Pairing the items to the new rows by
        position afterwards -- ``zip(items, Label.objects.order_by('pk'))`` --
        assumed ``bulk_create`` inserted in input order and that the new primary
        keys sorted the same way, which the database API does not promise; when
        it fails, every planting label points at the wrong species and nothing
        raises (issue 010).
        """
        items = json.loads(request.body)
        Label.objects.all().delete()
        labels_by_external_id = {}
        for item in items:
            label = Label.objects.create(species_id=item['id'],
                                         photo_id=item['photo_pk'],
                                         visible=item['visible'])
            for external_id in item['external_ids']:
                labels_by_external_id[external_id] = label
        plantings = (Planting.objects
                     .public_planted()
                     .filter(observation__external_id__in=
                             labels_by_external_id))
        for planting in plantings:
            planting.label = labels_by_external_id[
                planting.observation.external_id]
            planting.save()
        return HttpResponse('OK', content_type='text/plain')


class PlantedSpecies(TemplateResponseMixin, View):
    template_name = 'kasvimuseo/reports/planted-species.html'

    def get_context_data(self, queryset):
        return {'pages': [self._get_single_context_data(species)
                          for species in queryset],
                'base_template': ('kasvimuseo/reports/%s'
                                  % self.base_template_name)}

    def _get_single_context_data(self, species):
        beds = list(Bed.objects
                    .filter(planting__observation__species=species,
                            public=True)
                    .distinct())
        for bed in beds:
            bed.plantings = (bed.planting_set
                             .filter(observation__species=species)
                             .exclude(removal_date__isnull=False))
        planted_observations = list(
            Observation.objects
            .filter(species=species, planting__isnull=False)
            .order_by('origin__name')
            .distinct())
        origins = set(observation.origin.name
                      for observation in planted_observations)
        local_names = []
        for observation in planted_observations:
            if observation.nickname:
                local_names.append(observation.nickname)

        def get_adjacent_species(order, comparison):
            adjacent_species = list(
                Species.objects
                .public_planted()
                .order_by(order + 'name_fi')
                .filter(**{'name_fi__' + comparison: species.name_fi}))[:1]
            if adjacent_species:
                return adjacent_species[0]

        ctx = {'species': species,
               'previous': get_adjacent_species('-', 'lt'),
               'next': get_adjacent_species('', 'gt'),
               'beds': beds,
               'origins': origins,
               'planted_observations': planted_observations,
               'local_names': local_names}
        return ctx

    def get(self, request, species_external_ids):
        extid_list = species_external_ids.split(',')
        queryset = Species.objects.filter(external_id__in=extid_list)
        if not queryset.exists():
            # A list that matches nothing at all is a dead link, not a report;
            # a partial match still renders what it found. See docs/issues/007.
            raise Http404('No Species matches any of the given external ids.')
        context = self.get_context_data(queryset)
        if 'HTTP_REFERER' in request.META:
            context['next'] = request.META['HTTP_REFERER']
        return self.render_to_response(context)


class PlantedSpeciesPrintable(PlantedSpecies):
    base_template_name = 'planted-species-base-printable.html'


class PlantedSpeciesCompact(PlantedSpecies):
    base_template_name = 'planted-species-base-compact.html'


def planted_observation(request, observation_external_id):
    # Museum numbers are not unique -- a handful of them are shared by two
    # observations -- so ``get_object_or_404`` raised ``MultipleObjectsReturned``
    # instead of answering. Order explicitly and take the first match, so the
    # same number always renders the same page. See docs/issues/041.
    observations = (Observation.objects
                    .filter(external_id=observation_external_id)
                    .order_by('pk'))[:1]
    if not observations:
        raise Http404('No Observation matches the given museum number.')
    observation = observations[0]
    plantings = observation.planting_set.all()
    beds = [planting.bed for planting in plantings]
    texts = []
    if observation.history:
        texts.append(observation.history)
    if observation.stories:
        texts.append(observation.stories)

    return render_to_response(
        'kasvimuseo/reports/planted-observation.html',
        {'species': observation.species,
         'observation': observation,
         'plantings': plantings,
         'beds': beds,
         'origin': observation.origin,
         'texts': texts},
        RequestContext(request))


class BedMap(DetailView):
    model = Bed
    template_name = 'kasvimuseo/bed-map.html'

    def get_context_data(self, **kwargs):
        return super(BedMap, self).get_context_data(
            bed_depth=40, **kwargs)
