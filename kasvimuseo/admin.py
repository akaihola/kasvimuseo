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
    fieldsets=((None,
                {'fields': ('external_id',
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
                            'spacing',)}),
    ),
)

admin.site.register(
    Location,
    inlines=[LocationContactInline, ObservationInline],
    save_on_top=True,
    exclude=('external_id', 'contacts',),
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
    fieldsets=((_(u'Basic information'),
                {'fields': ('external_id',
                            'origin',
                            'species',
                            'date',),
                 'classes': ('column',)}),
               (_(u'Extra information'),
                {'fields': ('characteristics',
                            'nickname',
                            'history',
                            'stories',
                            'pictures',
                            'environment',),
           'classes': ()})),
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
    fieldsets=((None,
                {'fields': ('planting', 'date', 'description', 'count',),
                 'description': _(u'Erityiset hoitotapahtumat, '
                                  u'suojaus, '
                                  u'harvennus, '
                                  u'sato, '
                                  u'siementen keruu, '
                                  u'taimien kasvatus, '
                                  u'myynti jne.')}),
    ),
)


class ContactAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('last_name',
                    'first_name',
                    'phone',
                    'mobile',
                    'email',
                    'street',
                    'number',
                    'apartment',
                    'zipcode',
                    'city',
                    'description',)
    list_display_links = ('last_name', 'first_name')
    fieldsets = (
        (_(u'Basic information'), {
            'fields': ('last_name',
                       'first_name',
                       'phone',
                       'mobile',
                       'email',
                       'description',),
            'classes': ('fieldset_column',)
        }),
        (_(u'Address'), {
            'fields': ('street',
                       'number',
                       'apartment',
                       'zipcode',
                       'city',)
        }),
    )

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Contact, ContactAdmin)


admin.site.register(
    Plot,
    inlines=[BedInline],
    save_on_top=True,
)

admin.site.register(
    Bed,
    save_on_top=True,
)
