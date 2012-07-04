from collections import defaultdict
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import ListView, View
from django.views.generic.base import TemplateResponseMixin

from kasvimuseo.models import Bed, Observation, Species


class PlantedSpeciesList(ListView):
    template_name = 'kasvimuseo/reports/planted-species-list.html'
    model = Species

    # FIXME: .public-planted() is evaluated at import time!
    queryset = (model.objects
                .public_planted()
                .distinct()
                .order_by('name_fi'))


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
