from django.contrib import admin

from elements.participants.models import EntityParticipant

class EntityParticipantAdmin(admin.ModelAdmin):
    list_display = ('entity', 'person', 'role')
    search_fields = ('entity_id', 'person__user', 'role')
    raw_id_fields = ('person',)

admin.site.register(EntityParticipant, EntityParticipantAdmin)
