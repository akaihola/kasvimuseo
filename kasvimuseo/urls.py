from django.conf.urls.defaults import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from .views import (BedMap,
                    PlantedSpeciesCompact,
                    PlantedSpeciesLabels,
                    PlantedSpeciesLabelsApi,
                    PlantedSpeciesList,
                    PlantedSpeciesPrintable,
                    staff_only_api)

urlpatterns = patterns(
    'kasvimuseo.views',

    # pylint: disable=E1101
    #         Instance of <class> has no <member>

    url(regex=(r'^planted-species/$'),
        view=PlantedSpeciesList.as_view(),
        name='planted-species-list'),

    # Staff only, both of them (issue 052). ``post`` on the data endpoint
    # deletes every label and rebuilds the table from the request body, and
    # until this decorator was added anyone who knew the URL could run it: the
    # views carried no check and neither does the include in
    # ``ylaneenkasvit.urls``. The page is gated the way the admin gates its
    # own -- a login form in place of the page -- while the endpoint answers
    # 403, because a login form behind a 200 is not something axios can tell
    # from a saved sheet.
    url(regex=r'^planting-labels/$',
        view=staff_member_required(PlantedSpeciesLabels.as_view()),
        name='planting-label'),

    url(regex=r'^planting-labels/data/$',
        view=staff_only_api(PlantedSpeciesLabelsApi.as_view()),
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
