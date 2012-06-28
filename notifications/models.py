# -*- coding:utf-8 -*-
import json

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string

from services.email import send_email
from users.models import Profile

class NotificationType(object):
    name = ''
    template = '' # path for template with notification html message

    @classmethod
    def recipients(cls, data):
        """ Return list of profile ids """
        raise NotImplemented

    @classmethod
    def context(cls, data):
        """ Return  """
        raise NotImplemented

    @classmethod
    def send(cls, data):
        """ This method should be called to initiate sending notifications to a list of recipients """
        recipient_ids = cls.recipients(data)
        data_str = json.dumps(data, ensure_ascii=False)
        notification = Notification.objects.create(type=cls.name, data=data_str)

        notification_recipients = [NotificationRecipient(notification=notification, recipient_id=id)
                for id in recipient_ids]
        NotificationRecipient.objects.bulk_create(notification_recipients)

        # Activate task for sending emails
        from notifications.tasks import send_notifications
        send_notifications.delay()

NOTIFICATIONS = {}

def register_notification(notification_type):
    """ Class decorator for registering notification types """
    NOTIFICATIONS[notification_type.name] = notification_type
    return notification_type

class Notification(models.Model):
    type = models.CharField(max_length=20)
    data = models.TextField()
    time = models.DateTimeField(auto_now=True, db_index=True)

    def __unicode__(self):
        return self.type

class NotificationRecipient(models.Model):
    notification = models.ForeignKey(Notification, related_name='recipients')
    recipient = models.ForeignKey(Profile, related_name='notifications')
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

def notify_user(profile_id):
    nrs = NotificationRecipient.objects.select_related('notification') \
            .filter(recipient=profile_id, email_sent=False, is_read=False) \
            .order_by('notification__time')

    notifications = []
    for nr in nrs:
        notification_type = NOTIFICATIONS[nr.notification.type]
        data = json.loads(nr.notification.data)
        ctx = notification_type.context(data)
        ctx.update({'URL_PREFIX': settings.URL_PREFIX, 'STATIC_URL': settings.STATIC_URL})
        notifications.append(render_to_string(notification_type.template, ctx))

    if len(notifications) > 0:
        profile = Profile.objects.select_related('user').get(id=profile_id)
        send_email(profile, u'Активность на площадке Гракон', 'letters/notifications.html',
                {'notifications': notifications}, 'notification', 'noreply')

        nrs = NotificationRecipient.objects.filter(id__in=[nr.id for nr in nrs]) \
                .update(email_sent=True)
