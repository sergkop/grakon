# -*- coding:utf-8 -*-
from datetime import datetime

from django.db import models

from users.models import Profile

# TODO: model to manage subscription + settings for receiving letters

# TODO: add retry status (if quota was exceeded)
EMAIL_STATUSES = (
    ('unsent', u'Еще не отправлено'),
    ('sent', u'Отправлено'),
    ('rejected', u'Не принятно'),
    ('bounce', u'Вернулось'),
    ('spam', u'Спам'),
)

class Email(models.Model):
    recipient = models.ForeignKey(Profile, blank=True, null=True, default=None)
    hash = models.CharField(max_length=30, db_index=True)
    type = models.CharField(max_length=20, db_index=True)
    raw_msg = models.TextField()
    from_email = models.CharField(max_length=15, db_index=True) # key to get email from EMAILS
    to_email = models.EmailField(db_index=True)

    time = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=9, choices=EMAIL_STATUSES, default='unsent', db_index=True)
    is_read = models.BooleanField(default=False)
    read_time = models.DateTimeField(db_index=True, blank=True, null=True)
    error = models.TextField()

    priority = models.IntegerField(db_index=True) # Used by celery to prioritise tasks

    def update_status(self, status, error=''):
        """ Update status (other than 'unsent') """
        self.status = status
        self.error = error
        self.raw_msg = ''
        self.save()

    def mark_read(self):
        self.read_time = datetime.now()
        self.is_read = True
        self.save()

    def send(self):
        from services.utils.email import send_email_task
        send_email_task(self)
