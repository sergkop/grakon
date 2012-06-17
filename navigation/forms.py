# -*- coding:utf-8 -*-
from django import forms
from django.forms.widgets import Textarea

from grakon.utils import escape_html
from elements.utils import form_helper
from services.email import send_email

class FeedbackForm(forms.Form):
    name = forms.CharField(label=u'Ваше имя')
    email = forms.EmailField(label=u'Электронная почта')
    body = forms.CharField(label=u'Сообщение', widget=Textarea())

    helper = form_helper('feedback', u'Отправить')

    def __init__(self, request, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.request.profile:
            del self.fields['name']
            del self.fields['email']

    def send(self):
        ctx = {
            'message': escape_html(self.cleaned_data['body']),
            'profile': self.request.profile,
            'hide_signature': True,
        }

        if not self.request.profile:
            ctx['name'] = self.cleaned_data['name']
            ctx['email'] = self.cleaned_data['email']

        send_email(None, u'[ОБРАТНАЯ СВЯЗЬ]', 'letters/feedback.html', ctx, 'feedback', 'noreply')
