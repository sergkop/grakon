# -*- coding:utf-8 -*-
import datetime
import random
import re

from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils.hashcompat import sha_constructor

from services.email import send_email

ACTIVATED = 'ALREADY_ACTIVATED'
SHA1_RE = re.compile('^[a-f0-9]{40}$')

class ActivationManager(models.Manager):
    def activate_user(self, activation_key):
        if SHA1_RE.search(activation_key):
            try:
                profile = self.filter(activation_key=activation_key).latest()
            except self.model.DoesNotExist:
                return False

            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()

                profile.activation_key = ACTIVATED
                profile.save()
                return user

        return False

    @transaction.commit_on_success
    def init_activation(self, user):
        # The activation key is a SHA1 hash, generated from a combination of the username and a random salt
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        activation_key = sha_constructor(salt+user.username).hexdigest()

        registration_profile = self.create(user=user, activation_key=activation_key)
        return registration_profile.send_activation_email()

    def delete_expired_users(self):
        """
        Remove expired instances of ActivationProfile and their associated User's.

        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupregistration``.

        If you have a troublesome User and wish to disable their
        account while keeping it in the database, simply delete the
        associated ActivationProfile; an inactive User which
        does not have an associated ActivationProfile will not
        be deleted.
        """
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


# TODO: drop it
#from social_auth.signals import pre_update
#from social_auth.backends.google import GoogleOAuth2

#def google_extra_values(sender, user, response, details, **kwargs):
#    return True

#pre_update.connect(google_extra_values, sender=GoogleOAuth2)
