from django.contrib import admin

from elements.admins.models import EntityAdmin

class EntityAdminAdmin(admin.ModelAdmin):
    list_display = ('entity', 'admin')
    search_fields = ('entity_id', 'admin__username')
    raw_id_fields = ('admin',)
    
admin.site.register(EntityAdmin, EntityAdminAdmin)
