from django.contrib import admin

from elements.followers.models import EntityFollower

class EntityFollowerAdmin(admin.ModelAdmin):
    list_display = ('entity', 'follower')
    search_fields = ('entity_id', 'follower__username')

admin.site.register(EntityFollower, EntityFollowerAdmin)
