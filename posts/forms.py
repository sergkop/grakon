# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.utils import form_helper
from posts.models import EntityPost

class PostForm(forms.ModelForm):
    class Meta:
        model = EntityPost

    helper = form_helper('', u'Сохранить')
    helper.layout = Layout(Fieldset('', 'content', 'opinion'))
