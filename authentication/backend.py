# -*- coding:utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailAuthenticationBackend(ModelBackend):
    """ Used to allow authentication with email instead of username """
    supports_inactive_user = False

    def authenticate(self, username, password=None):
        # TODO: what if there are several users with the same email?
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
