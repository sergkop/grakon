# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.resources.forms import resources_init
from elements.utils import form_helper
from users.models import Profile

@resources_init
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'username')

    helper = form_helper('', u'Сохранить')
    helper.layout = Layout(
        Fieldset('', 'first_name', 'last_name', 'show_name',
                'resources1', 'about'),
    )
