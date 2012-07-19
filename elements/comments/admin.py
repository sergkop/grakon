from django.contrib import admin

from elements.comments.models import EntityComment

class EntityCommentAdmin(admin.ModelAdmin):
    list_display = ('entity', 'person', 'comment')
    search_fields = ('entity_id', 'person__user')
    raw_id_fields = ('parent', 'person')

admin.site.register(EntityComment, EntityCommentAdmin)
