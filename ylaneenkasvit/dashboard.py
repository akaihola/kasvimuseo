"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'ylaneenkasvit.dashboard.CustomIndexDashboard'
"""

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard

from kasvimuseo.models import Bed


class CustomIndexDashboard(Dashboard):
    """Custom index dashboard for kasvit.ambitone.com"""

    def init_with_context(self, context):
        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            u'',
            collapsible=True,
            column=1,
            css_classes=('collapse',),
            models=('kasvimuseo.models.Species',
                    'kasvimuseo.models.Location',
                    'kasvimuseo.models.Contact',
                    'kasvimuseo.models.Plot',
                    'kasvimuseo.models.Bed',),
        ))

        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            u'',
            collapsible=True,
            column=1,
            css_classes=('collapse',),
            models=('kasvimuseo.models.Observation',
                    'kasvimuseo.models.Planting',
                    'kasvimuseo.models.Care',),
        ))

        # append an app list module for "Photos"
        self.children.append(modules.ModelList(
            u'',
            collapsible=True,
            column=1,
            css_classes=('collapse',),
            models=('photologue.models.Gallery',
                    'photologue.models.Photo',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Administration'),
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
        ))

        # append a link list module for the reports and tools which live
        # outside the admin, and for the pages they are reached through
        self.children.append(modules.LinkList(
            _('Reports and tools'),
            column=2,
            collapsible=False,
            children=(
                (_('Planted species'),
                 reverse('planted-species-list'),
                 False,
                 _('The mobile plant list: every publicly planted species '
                   'with its photo, leading to the species pages')),
                (_('Species sheets'),
                 reverse('admin:kasvimuseo_species_changelist'),
                 False,
                 _('Tick the species in the list and run the '
                   '"Create Species Sheets" action')),
                (_('Planting labels'),
                 reverse('planting-label'),
                 False,
                 _('Choose the photo and the visibility of each label to be '
                   'printed for the beds')),
                (_('Photo galleries'),
                 reverse('pl-gallery-archive'),
                 False,
                 _('The public Photologue galleries')),
            ),
        ))

        # append a link list module with the map of every bed
        self.children.append(modules.LinkList(
            _('Bed maps'),
            column=2,
            collapsible=True,
            children=[(force_text(bed),
                       reverse('bed-map', kwargs={'pk': bed.pk}))
                      for bed in (Bed.objects
                                  .select_related('plot')
                                  .order_by('plot__name', 'name'))],
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))


