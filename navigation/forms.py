# -*- coding:utf-8 -*-
from django import forms
from django.forms.widgets import Textarea

from elements.utils import form_helper
from services.email import send_email

class FeedbackForm(forms.Form):
    name = forms.CharField(label=u'Ваше имя')
    email = forms.CharField(label=u'Электронная почта')
    body = forms.CharField(label=u'Сообщение', widget=Textarea(attrs={'style': 'width:50%;'}))

    helper = form_helper('feedback', u'Отправить')

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if self.request.user.is_authenticated():
            del self.fields['name']
            del self.fields['email']

    # TODO: fix it
    def send(self):
        # TODO: escape html in message
        ctx = {
            'message': self.cleaned_data['body'],
            #'user': self.request.user,
        }
        ctx['name'] = self.cleaned_data.get('name', '')
        ctx['email'] = self.cleaned_data.get('email', '')
        if self.request.user.is_authenticated():
            ctx['link']  = u'%s%s' % (settings.URL_PREFIX, reverse(
                    'profile', kwargs={'username': self.request.user.username}))

        send_email(None, u'[ОБРАТНАЯ СВЯЗЬ]', template, ctx, 'feedback', 'noreply')
