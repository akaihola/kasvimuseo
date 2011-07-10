from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from kasvimuseo.models import (
    Bed, Care, Contact, Location, Observation, Planting, Plot, Species)
from kasvimuseo.views import PlantedSpecies


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


def planted_species_report(modeladmin, request, queryset):
    external_ids = queryset.values_list('external_id', flat=True)
    external_ids_param = u','.join(unicode(external_id)
                                   for external_id in external_ids)
    url = reverse('planted-species',
                  kwargs={'species_external_ids': external_ids_param})
    return HttpResponseRedirect(url)
planted_species_report.short_description = _(u'Create Species Sheets')


class SpeciesAdmin(admin.ModelAdmin):
    inlines = [ObservationInline]
    save_on_top = True
    list_display = (
        edit,
        'external_id',
        'name_fi',
        'genus',
        'group',
        'species',
        'subspecies',
        'variety',
        'type',
        'height',
        'width',
        'spacing',
        'flower_color',
        'flowering_time',
        'lighting',
        'substrate',
        'additional_info',)
    list_filter = 'type',
    fieldsets = (None,
                 {'fields': ('external_id',
                             'name_fi',
                             'genus',
                             'group',
                             'species',
                             'subspecies',
                             'variety',
                             'type',
                             'height',
                             'spacing',
                             'width',
                             'flower_color',
                             'flowering_start',
                             'flowering_end',
                             'lighting',
                             'substrate',
                             'additional_info',)}),
    actions = [planted_species_report]

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Species, SpeciesAdmin)


class LocationAdmin(admin.ModelAdmin):
    inlines = LocationContactInline, ObservationInline,
    save_on_top = True
    exclude = 'external_id', 'contacts',
    list_display = (edit,
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
                    )

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Location, LocationAdmin)


class PlantingAdmin(admin.ModelAdmin):
    inlines = [CareInline]
    save_on_top = True
    list_display = (edit,
                    'observation',
                    'bed',
                    'planting_date',
                    'count',
                    'last_care_date',
                    'last_care_description',
                    'last_care_count',
                    'removal_date',)
    list_filter = 'observation__origin', 'bed', 'planting_date',

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Planting, PlantingAdmin)


class ObservationAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (edit,
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
                    'environment',)
    list_filter = 'origin', 'species__type', 'date',
    fieldsets = ((_(u'Basic information'),
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
                   'classes': ()}))

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Observation, ObservationAdmin)


class CareAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (edit,
                    'date',
                    'planting',
                    'description',
                    'count',)
    list_filter = 'planting__bed', 'date',
    fieldsets = ((None,
                  {'fields': ('planting', 'date', 'description', 'count',),
                   'description': _(u'Erityiset hoitotapahtumat, '
                                    u'suojaus, '
                                    u'harvennus, '
                                    u'sato, '
                                    u'siementen keruu, '
                                    u'taimien kasvatus, '
                                    u'myynti jne.')}),)

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Care, CareAdmin)


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


class PlotAdmin(admin.ModelAdmin):
    list_display = edit, 'name',
    inlines = BedInline,
    save_on_top = True

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Plot, PlotAdmin)


class BedAdmin(admin.ModelAdmin):
    list_display = edit, 'plot', 'name', 'description',
    save_on_top = True

    class Media:
        css = {'all': ('/media/kasvimuseo/css/kasvimuseo.admin.css',)}

admin.site.register(Bed, BedAdmin)
