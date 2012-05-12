# -*- coding:utf-8 -*-
from django import forms

from elements.forms import resources_init
from elements.utils import form_helper
from users.models import Profile

# TODO: change order of fields
@resources_init
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'username')

    helper = form_helper('', u'Сохранить')
