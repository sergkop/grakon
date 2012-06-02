from django.contrib import admin

from services.models import Email

class EmailAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'to_email', 'type', 'time', 'status', 'is_read', 'priority')
    ordering = ('-time',)
    search_fields = ('recipient__username', 'type', 'status')
    raw_id_fields = ('recipient',)

admin.site.register(Email, EmailAdmin)
