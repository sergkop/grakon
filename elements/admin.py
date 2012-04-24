from django.contrib import admin

from elements.models import EntityFollower, EntityLocation, EntityResource

class EntityFollowerAdmin(admin.ModelAdmin):
    list_display = ('entity', 'follower')
    search_fields = ('entity__id', 'follower__username')

class EntityLocationAdmin(admin.ModelAdmin):
    list_display = ('entity', 'location')
    search_fields = ('entity__id', 'location__id', 'location__name')
    raw_id_fields = ('location',)

class EntityResourceAdmin(admin.ModelAdmin):
    list_display = ('entity', 'resource')
    search_fields = ('entity__id', 'resource')

admin.site.register(EntityFollower, EntityFollowerAdmin)
admin.site.register(EntityLocation, EntityLocationAdmin)
admin.site.register(EntityResource, EntityResourceAdmin)
