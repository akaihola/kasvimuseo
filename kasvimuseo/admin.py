from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from kasvimuseo.models import (
    Bed, Care, Contact, Location, Observation, Planting, Plot, Species)


def edit(instance):
    return _('Edit')
edit.short_description = _(u'Edit')


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
        edit,
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
    list_filter=('type',),
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
                            'flowering_start',
                            'flowering_end',
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
        edit,
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
)


class PlantingAdmin(admin.ModelAdmin):
    inlines = [CareInline]
    save_on_top = True
    list_display = (edit,
                    'observation',
                    'bed',
                    'planting_date',
                    'count',
                    'removal_date',)
    list_filter = 'observation__origin', 'bed', 'planting_date',

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Planting, PlantingAdmin)


admin.site.register(
    Observation,
    save_on_top=True,
    list_display=(
        edit,
        'external_id',
        'name_fi',
        'genus',
        'species_species',
        'subspecies',
        'variation',
        'origin',
        'date',
        'characteristics',
        'nickname',
        'history',
        'stories',
        'pictures',
        'environment',
    ),
    list_filter=('origin', 'species__type', 'date',),
    fieldsets=((_(u'Basic information'),
                {'fields': ('external_id',
                            'origin',
                            'species',
                            'variation',
                            'date',),
                 'classes': ('fieldset_column',)}),
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
        edit,
        'date',
        'planting',
        'description',
        'count',
    ),
    list_filter=('planting__bed', 'date',),
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
    list_display = (edit,
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
                    'description',)
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
    list_display=(edit, 'name',),
    inlines=[BedInline],
    save_on_top=True,
)

admin.site.register(
    Bed,
    list_display=(edit, 'plot', 'name', 'description',),
    save_on_top=True,
)
