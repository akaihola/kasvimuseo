# -*- encoding: utf-8 -*-

import os

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext, ugettext_lazy as _

from .forms import PhotoForm, SpeciesForm
from kasvimuseo.models import (
    Bed, Care, Contact, Location, Observation, Planting, Plot, Species)
from kasvimuseo.views import PlantedSpecies
from photologue.admin import PhotoAdmin as PhotologuePhotoAdmin
from photologue.models import Photo


ADMIN_CSS_PATH = '%scss/kasvimuseo.admin.css' % settings.STATIC_URL
CSS = {'all': (ADMIN_CSS_PATH,)}


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
    """Redirects to the printable report for the selected species.

    The report URL is keyed by ``external_id``, which the museum's own
    numbering fills in but the model leaves optional, so a species without one
    cannot appear in the report at all -- ``ObservationAdmin.page`` skips such
    rows for the same reason. Report on the ones that can be reported on, and
    name the ones left out; if that is all of them, there is no report to make.

    See docs/issues/009.
    """
    skipped = list(queryset.filter(external_id=None))
    external_ids = list(queryset.exclude(external_id=None)
                        .values_list('external_id', flat=True))
    if skipped:
        modeladmin.message_user(
            request,
            ugettext(u'Left out of the report, having no LajiNro: %s')
            % u', '.join(unicode(species) for species in skipped))
    if not external_ids:
        modeladmin.message_user(
            request,
            ugettext(u'None of the selected species has a LajiNro, '
                     u'so there is no report to create.'))
        return
    external_ids_param = u','.join(unicode(external_id)
                                   for external_id in external_ids)
    url = reverse('planted-species',
                  kwargs={'species_external_ids': external_ids_param})
    return HttpResponseRedirect(url)
planted_species_report.short_description = _(u'Create Species Sheets')


class SpeciesAdmin(admin.ModelAdmin):
    inlines = [ObservationInline]
    form = SpeciesForm
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
        'cultivation_history',
        'type',
        'height',
        'width',
        'spacing',
        'flower_color',
        'flowering_time',
        'lighting',
        'substrate',
        'additional_info',
        "photo_image",
    )
    list_filter = ("type",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "external_id",
                    "name_fi",
                    "genus",
                    "group",
                    "species",
                    "subspecies",
                    "variety",
                    "cultivation_history",
                    "type",
                    "height",
                    "spacing",
                    "width",
                    "flower_color",
                    "flowering_start",
                    "flowering_end",
                    "lighting",
                    "substrate",
                    "additional_info",
                    # Last, because it is the one field here the auto-attach
                    # receiver also writes; ``SpeciesForm`` limits the choices
                    # to this species' photos and says so (issue 037).
                    "photo",
                )
            },
        ),
    )
    actions = [planted_species_report]

    class Media:
        css = CSS

    def photo_image(self, obj):
        return os.path.basename(obj.photo.image.path) if obj.photo else ""

    photo_image.short_description = "photo_image"


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
        css = CSS
admin.site.register(Location, LocationAdmin)


class PlantingAdmin(admin.ModelAdmin):
    inlines = [CareInline]
    save_on_top = True
    list_display = (edit,
                    'observation_external_id',
                    'observation',
                    'bed',
                    'planting_date',
                    'count',
                    'last_care_date',
                    'last_care_description',
                    'last_care_count',
                    'removal_date',
                    'coordinates',)
    list_filter = 'observation__origin', 'bed', 'planting_date',
    ordering = 'observation__external_id',

    def coordinates(self, obj):
        return u'({0}cm,{1}cm)<br>{2}×{3}cm'.format(
            obj.distance_left, obj.distance_front,
            obj.width, obj.depth)
    coordinates.short_description = _(u'(left,front) width×depth')
    coordinates.allow_tags = True

    class Media:
        css = CSS
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
                    'notes',
                    'environment',
                    'page',)
    list_filter = 'origin', 'species__type', 'date',

    def page(self, obj):
        """Links the public page of the observation, as ``BedAdmin`` does.

        The URL is keyed by ``external_id``, which the museum's own numbering
        fills in but the model leaves optional, so an observation without one
        has no page to link.
        """
        if obj.external_id is None:
            return u''
        url = reverse('planted-observation', args=[obj.external_id])
        return u'<a href="{0}">{1}</a>'.format(url, _(u'page'))
    page.short_description = _(u'show page')
    page.allow_tags = True

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
                              'notes',
                              'environment',),
                   'classes': ()}))

    class Media:
        css = CSS
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
        css = CSS
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
        css = CSS
admin.site.register(Contact, ContactAdmin)


class PlotAdmin(admin.ModelAdmin):
    list_display = edit, 'name',
    inlines = BedInline,
    save_on_top = True

    class Media:
        css = CSS
admin.site.register(Plot, PlotAdmin)


class BedAdmin(admin.ModelAdmin):
    list_display = edit, 'plot', 'name', 'description', 'public', 'map'
    save_on_top = True

    def map(self, obj):
        url = reverse('bed-map', kwargs={'pk': obj.pk})
        label = _(u'map')
        return u'<a href="{0}">{1}</a>'.format(url, label)
    map.short_description = _(u'show map')
    map.allow_tags = True

    class Media:
        css = CSS
admin.site.register(Bed, BedAdmin)


class SpeciesInline(admin.TabularInline):
    model = Species
    verbose_name_plural = _(u'Species to which the photo is attached')
    fields = 'name_fi',


class PhotoAdmin(PhotologuePhotoAdmin):
    list_display = ['image_filename' if field_name == 'title' else field_name
                    for field_name in PhotologuePhotoAdmin.list_display]
    form = PhotoForm
    inlines = SpeciesInline,

    def image_filename(self, obj):
        return obj.image.name.split('/')[-1]
    # Every photo is stored flat under ``photologue/photos/`` -- photologue's
    # ``get_storage_path`` joins PHOTOLOGUE_DIR, 'photos' and the file name --
    # so ``image`` is the file name behind one constant prefix, and ordering by
    # it is ordering by name. Issue 043.
    image_filename.admin_order_field = 'image'

    class Media:
        css = CSS

admin.site.unregister(Photo)
admin.site.register(Photo, PhotoAdmin)
