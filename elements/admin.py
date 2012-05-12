from django.contrib import admin

from elements.models import EntityAdmin, EntityFollower, EntityLocation, EntityResource

class EntityAdminAdmin(admin.ModelAdmin):
    list_display = ('entity', 'admin')
    search_fields = ('entity_id', 'admin__username')
    raw_id_fields = ('admin',)

class EntityFollowerAdmin(admin.ModelAdmin):
    list_display = ('entity', 'follower')
    search_fields = ('entity_id', 'follower__username')

class EntityLocationAdmin(admin.ModelAdmin):
    list_display = ('entity', 'location')
    search_fields = ('entity_id', 'location__id', 'location__name')
    raw_id_fields = ('location',)

class EntityResourceAdmin(admin.ModelAdmin):
    list_display = ('entity', 'resource')
    search_fields = ('entity_id', 'resource')

admin.site.register(EntityAdmin, EntityAdminAdmin)
admin.site.register(EntityFollower, EntityFollowerAdmin)
admin.site.register(EntityLocation, EntityLocationAdmin)
admin.site.register(EntityResource, EntityResourceAdmin)
