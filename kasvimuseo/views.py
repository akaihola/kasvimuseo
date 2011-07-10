from collections import defaultdict
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateResponseMixin, View

from kasvimuseo.models import Bed, Observation, Species


class PlantedSpecies(TemplateResponseMixin, View):
    template_name = 'kasvimuseo/reports/planted-species.html'

    def get_context_data(self, queryset):
        return {'pages': [self._get_single_context_data(species)
                          for species in queryset]}

    def _get_single_context_data(self, species):
        beds = list(Bed.objects
                    .filter(planting__observation__species=species)
                    .distinct())
        bed_dict = dict((bed.pk, bed) for bed in beds)
        for bed in beds:
            bed.planted_observations = []
        planted_observations = list(
            Observation.objects
            .filter(species=species, planting__isnull=False)
            .distinct())
        origins = set(observation.origin.name
                      for observation in planted_observations)
        local_names = []
        for observation in planted_observations:
            for planting in observation.planting_set.all():
                bed = bed_dict.get(planting.bed_id)
                if bed:
                    bed.planted_observations.append(observation)
            if observation.nickname:
                local_names.append(observation.nickname)

        return {'species': species,
                'beds': beds,
                'origins': origins,
                'planted_observations': planted_observations,
                'local_names': local_names}

    def get(self, request, species_external_ids):
        extid_list = species_external_ids.split(',')
        queryset = Species.objects.filter(external_id__in=extid_list)
        context = self.get_context_data(queryset)
        if 'HTTP_REFERER' in request.META:
            context['next'] = request.META['HTTP_REFERER']
        return self.render_to_response(context)


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
