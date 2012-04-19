# -*- coding:utf-8 -*-
from django import forms

from elements.utils import clean_html, form_helper
from users.models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('main_location', 'user', 'username')

    helper = form_helper('', u'Сохранить')

    def clean_about(self):
        return clean_html(self.cleaned_data['about'])
