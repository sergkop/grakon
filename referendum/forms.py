# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.utils import form_helper
from referendum.models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question

    helper = form_helper('', u'Добавить')
    #helper.layout = Layout(
    #    Fieldset('', 'title',),
    #)
