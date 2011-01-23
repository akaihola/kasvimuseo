from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from kasvimuseo.models import (
    Bed, Care, Contact, Location, Observation, Planting, Plot, Species)


class CareInline(admin.TabularInline):
    model = Care
    verbose_name_plural = _(u'Erityiset hoitotapahtumat, '
                            u'suojaus, '
                            u'harvennus, '
                            u'sato, '
                            u'siementen keruu, '
                            u'taimien kasvatus, '
                            u'myynti jne.')
 

class ObservationInline(admin.StackedInline):
    model = Observation
    extra = 1


class LocationContactInline(admin.TabularInline):
    model = Location.contacts.through


class BedInline(admin.TabularInline):
    model = Bed


admin.site.register(
    Species,
    inlines=[ObservationInline],
    save_on_top=True,
    list_display=(
        'external_id',
        'name_fi',
        'genus',
        'group',
        'species',
        'subspecies',
        'variety',
        'name_sv',
        'name_local',
        'abbr_fi',
        'abbr_scientific',
        'type',
        'height',
        'width',
        'flower_color',
        'flowering_time',
        'substrate',
        'spacing',),
    list_display_links=('external_id', 'name_fi'),
)

admin.site.register(
    Location,
    inlines=[LocationContactInline, ObservationInline],
    save_on_top=True,
    exclude=('contacts',),
    list_display=(
        'name',
        'alias',
        'village',
        'area',
        'street',
        'number',
        'apartment',
        'zipcode',
        'city',
        'history',
        #'contacts',
    ),
    list_display_links=('name',)
)

admin.site.register(
    Planting,
    inlines=[CareInline],
    save_on_top=True,
    list_display=(
        'observation',
        'bed',
        'planting_date',
        'count',
        'removal_date',),
)

admin.site.register(
    Observation,
    save_on_top=True,
    list_display=(
        'external_id',
        'name_fi',
        'genus',
        'species_species',
        'subspecies',
        'origin',
        'date',
        'characteristics',
        'nickname',
        'history',
        'stories',
        'pictures',
        'environment',
    ),
    list_display_links=('external_id', 'name_fi',),
)

admin.site.register(
    Care,
    save_on_top=True,
    list_display=(
        'date',
        'planting',
        'description',
        'count',
    ),
    list_display_links=('date', 'planting',),
)

admin.site.register(
    Contact,
    save_on_top=True,
    list_display=(
        'last_name',
        'first_name',
        'phone',
        'mobile',
        'email',
        'street',
        'number',
        'apartment',
        'zipcode',
        'city',
        'description',),
    list_display_links=('last_name', 'first_name'),
)

admin.site.register(
    Plot,
    inlines=[BedInline],
    save_on_top=True,
)

admin.site.register(
    Bed,
    save_on_top=True,
)
