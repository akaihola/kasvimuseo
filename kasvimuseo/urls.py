from django.conf.urls.defaults import patterns, url

from .views import (BedMap,
                    PlantedSpeciesCompact,
                    PlantedSpeciesLabels,
                    PlantedSpeciesLabelsApi,
                    PlantedSpeciesList,
                    PlantedSpeciesPrintable)

urlpatterns = patterns(
    'kasvimuseo.views',

    # pylint: disable=E1101
    #         Instance of <class> has no <member>

    url(regex=(r'^planted-species/$'),
        view=PlantedSpeciesList.as_view(),
        name='planted-species-list'),

    url(regex=(r'^planted-species-printable/$'),
        view=PlantedSpeciesList.as_view(extra_context={"printable": True}),
        name='planted-species-list-printable'),

    url(regex=r'^planting-labels/$',
        view=PlantedSpeciesLabels.as_view(),
        name='planting-label'),

    url(regex=r'^planting-labels/data/$',
        view=PlantedSpeciesLabelsApi.as_view(),
        name='planting-label-data'),

    url(regex=(r'^planted-species-compact/'
               r'(?P<species_external_ids>[\d,]+)/$'),
        view=PlantedSpeciesCompact.as_view(),
        name='planted-species-compact'),

    url(regex=(r'^planted-species-printable/'
               r'(?P<species_external_ids>[\d,]+)/$'),
        view=PlantedSpeciesPrintable.as_view(),
        name='planted-species'),

    url(regex=r'^planted-observation/(\d+)/$',
        view='planted_observation',
        name='planted-observation'),

    url(regex=r'^map/(?P<pk>\d+)/$',
        view=BedMap.as_view(),
        name='bed-map'),
)
