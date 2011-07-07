from django.conf.urls.defaults import patterns, url

from .views import PlantedSpecies


urlpatterns = patterns(
    'kasvimuseo.views',

    url(regex=(r'^planted-species/'
               r'(?P<species_external_ids>[\d,]+)/$'),
        view=PlantedSpecies.as_view(),
        name='planted-species'),

    url(regex=r'^planted-observation/(\d+)/$',
        view='planted_observation',
        name='planted-observation'),
)
