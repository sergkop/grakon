from django.contrib import admin

from posts.models import EntityPost

class EntityPostAdmin(admin.ModelAdmin):
    list_display = ('entity', 'profile', 'content', 'opinion')
    ordering = ('-time',)
    search_fields = ('entity_id', 'profile__username')
    raw_id_fields = ('profile',)

admin.site.register(EntityPost, EntityPostAdmin)
