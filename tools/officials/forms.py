# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.locations.forms import location_init
from elements.utils import form_helper
from tools.officials.models import Official

@location_init(False, u'Место работы')
class OfficialForm(forms.ModelForm):
    class Meta:
        model = Official

    helper = form_helper('', u'Сохранить')
    helper.layout = Layout(
        Fieldset(u'Персональные данные', 'last_name', 'first_name', 'middle_name',
                'post', 'place', 'email', 'telephone'),
        Fieldset(u'География', 'location_select', 'address'),
        Fieldset(u'', 'about'),
    )
