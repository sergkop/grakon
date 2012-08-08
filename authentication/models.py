# -*- coding:utf-8 -*-
import datetime
import random

from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils.hashcompat import sha_constructor

from services.email import send_email

ACTIVATED = 'ALREADY_ACTIVATED'

class ActivationManager(models.Manager):
    @transaction.commit_on_success
    def init_activation(self, user):
        # The activation key is a SHA1 hash, generated from a combination of the username and a random salt
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        activation_key = sha_constructor(salt+user.username).hexdigest()

        registration_profile = self.create(user=user, activation_key=activation_key)
        return registration_profile.send_activation_email()

    def delete_expired_users(self):
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()

class ActivationProfile(models.Model):
    user = models.ForeignKey(User)
    activation_key = models.CharField(max_length=40)
    date = models.DateTimeField(auto_now_add=True, null=True)

    objects = ActivationManager()

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        return u'Activation information for %s' % self.user

    def activation_key_expired(self):
        """ Boolean showing whether this activation key has expired """
        expiration_date = (self.user.date_joined+datetime.timedelta(days=5)).replace(tzinfo=None)
        return self.activation_key==ACTIVATED or (expiration_date<=datetime.datetime.utcnow())

    def send_activation_email(self):
        send_email(self.user.get_profile(), u'Активация учетной записи на grakon.org', 'letters/activation_email.html',
                {'activation_key': self.activation_key}, 'activation', 'noreply')

    def activate(self):
        if not self.activation_key_expired():
            self.user.is_active = True
            self.user.save()

            self.activation_key = ACTIVATED
            self.save()
