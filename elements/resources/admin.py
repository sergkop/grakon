from django.contrib import admin

from elements.resources.models import EntityResource

class EntityResourceAdmin(admin.ModelAdmin):
    list_display = ('entity', 'resource')
    search_fields = ('entity_id', 'resource')

admin.site.register(EntityResource, EntityResourceAdmin)
