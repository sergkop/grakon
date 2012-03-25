# -*- coding:utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailAuthenticationBackend(ModelBackend):
    """ Used to allow authentication with email instead of username """
    def authenticate(self, username, password=None):
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
