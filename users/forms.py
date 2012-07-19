# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.resources.forms import resources_init
from elements.utils import form_helper
from users.models import Message, Profile

@resources_init
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)

    helper = form_helper('', u'Сохранить')
    helper.layout = Layout(
        Fieldset('', 'first_name', 'last_name', 'resources1', 'about'),
    )

class MessageForm(forms.ModelForm):
    body = forms.CharField(label=u'Сообщение', widget=forms.Textarea(attrs={'rows': '6'}))

    class Meta:
        model = Message
        fields = ('title', 'body', 'show_email')
