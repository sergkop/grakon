# -*- coding:utf-8 -*-
from django import forms

from elements.forms import location_init
from elements.utils import form_helper
from tools.officials.models import Official

@location_init(False, u'Место работы')
class OfficialForm(forms.ModelForm):
    class Meta:
        model = Official

    helper = form_helper('', u'Сохранить')
