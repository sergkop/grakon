from django.contrib import admin

from elements.models import EntityLocation, EntityResource

class EntityResourceAdmin(admin.ModelAdmin):
    list_display = ('entity', 'resource')
    search_fields = ('entity__id', 'resource')

class EntityLocationAdmin(admin.ModelAdmin):
    list_display = ('entity', 'location')
    search_fields = ('entity__id', 'location__id', 'location__name')
    raw_id_fields = ('location',)

admin.site.register(EntityResource, EntityResourceAdmin)
admin.site.register(EntityLocation, EntityLocationAdmin)
