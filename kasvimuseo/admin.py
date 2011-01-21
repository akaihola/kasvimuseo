from django.contrib import admin

from kasvimuseo.models import (
    Species, Location, Observation, Planting, Care, Contact)


class CareInline(admin.TabularInline):
    model = Care


class ObservationInline(admin.TabularInline):
    model = Observation


admin.site.register(Species, inlines=[ObservationInline])
admin.site.register(Location)
admin.site.register(Planting, inlines=[CareInline])

admin.site.register(Observation)
admin.site.register(Care)
admin.site.register(Contact)
