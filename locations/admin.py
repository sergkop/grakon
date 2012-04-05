from django.contrib import admin

from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'region', 'district')
    ordering = ('id',)
    search_fields = ('id', 'name')
    raw_id_fields = ('country', 'region', 'district')

admin.site.register(Location, LocationAdmin)
