# pylint: disable=E1101
#         Instance has no 'X' method/attribute
# pylint: disable=W0142
#         Used * or ** magic
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import View, ListView
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.detail import DetailView

from kasvimuseo.models import Bed, Observation, Species, Label
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


class PlantedSpeciesLabelsApi(View):
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

    @staticmethod
    def get_species_data(species, photo_pks_and_urls_by_title):
        photo_pk, photo_alternatives = get_species_photo_info(
            species, photo_pks_and_urls_by_title)
        return {
            'id': species.pk,
            'name_fi': species.name_fi,
            'photo_pk': photo_pk,
            'all_photos': photo_alternatives,
            'external_ids': list(species.observation_set.public_planted()
                                 .order_by('external_id')
                                 .values_list('external_id', flat=True)),
            'genus': species.genus,
            'species': species.species,
            'group': species.group,
            'subspecies': species.subspecies,
            'nicknames': list(species.observation_set
                              .public_planted()
                              .values_list('nickname', flat=True)),
            'visible': True}

    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        # optimize the query
        queryset = (self.get_queryset()
                    .only('pk', 'name_fi', 'photo__image',
                          'genus', 'species', 'group', 'subspecies')
                    .select_related('photo', 'observation_set'))
        all_photos = get_photo_pks_and_urls_by_species()
        # noinspection PyUnresolvedReferences
        vue_data = {'object_list': [self.get_species_data(species, all_photos)
                                    for species in queryset]}
        return HttpResponse(json.dumps(vue_data),
                            content_type='application/json',
                            **kwargs)

    def post(self, request, *args, **kwargs):
        #old_labels = list(Label.objects.all())
        #Label.objects.all().delete()
        for item in json.loads(request.body):
            print(item)



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
        context = self.get_context_data(queryset)
        if 'HTTP_REFERER' in request.META:
            context['next'] = request.META['HTTP_REFERER']
        return self.render_to_response(context)


class PlantedSpeciesPrintable(PlantedSpecies):
    base_template_name = 'planted-species-base-printable.html'


class PlantedSpeciesCompact(PlantedSpecies):
    base_template_name = 'planted-species-base-compact.html'


def planted_observation(request, observation_external_id):
    observation = get_object_or_404(Observation,
                                    external_id=observation_external_id)
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
