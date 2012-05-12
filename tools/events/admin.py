from django.contrib import admin

from tools.events.models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'event_time')
    ordering = ('-time',)
    search_fields = ()

admin.site.register(Event, EventAdmin)
