from django.contrib import admin

from notifications.models import Notification, NotificationRecipient

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('type', 'data', 'time')
    ordering = ('-time',)

class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = ('notification', 'recipient', 'is_read', 'email_sent')
    ordering = ('-id',)
    raw_id_fields = ('recipient',)

admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationRecipient, NotificationRecipientAdmin)
