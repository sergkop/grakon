# -*- coding:utf-8 -*-
from django import forms

from elements.utils import form_helper
from users.models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'username', 'points', 'rating')

    helper = form_helper('', u'Сохранить')
