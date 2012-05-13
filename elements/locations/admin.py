from django.contrib import admin

from elements.locations.models import EntityLocation

class EntityLocationAdmin(admin.ModelAdmin):
    list_display = ('entity', 'location')
    search_fields = ('entity_id', 'location__id', 'location__name')
    raw_id_fields = ('location',)

admin.site.register(EntityLocation, EntityLocationAdmin)
