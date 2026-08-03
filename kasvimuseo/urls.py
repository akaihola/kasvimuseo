from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.clickjacking import xframe_options_exempt

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

    # Framed from another origin on purpose, which is why it is exempt from the
    # ``X-Frame-Options: SAMEORIGIN`` that ``XFrameOptionsMiddleware`` now puts
    # on every other response (issue 059). ``static/js/kasvimuseo/
    # planted-species-iframe.js`` is the script the museum's other site loads:
    # it writes an ``<iframe src="//kasvit.ambitone.com/kasvimuseo/
    # planted-species/">`` and resizes it from the ``postMessage`` that this
    # page's ``iframe-height-fix.js`` sends. ``SAMEORIGIN`` would leave that
    # frame blank. Exempting the two pages that are meant to be embedded costs
    # nothing worth having: both are public, read-only reports with no form to
    # submit and no session to act on, so there is nothing on them to trick a
    # logged-in user into clicking.
    url(regex=(r'^planted-species/$'),
        view=xframe_options_exempt(PlantedSpeciesList.as_view()),
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

    # The second framed page (issue 059): its base template,
    # ``planted-species-base-compact.html``, loads the same
    # ``iframe-height-fix.js``, which exists only to tell a parent frame how
    # tall to be. Reason as above.
    url(regex=(r'^planted-species-compact/'
               r'(?P<species_external_ids>[\d,]+)/$'),
        view=xframe_options_exempt(PlantedSpeciesCompact.as_view()),
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
