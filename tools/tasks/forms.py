# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.locations.forms import location_init
from elements.utils import form_helper
from tools.tasks.models import Task

@location_init(False, u'Место')
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task

    helper = form_helper('', u'Сохранить')
    helper.layout = Layout(
        Fieldset('', 'title', 'about', 'location_select'),
    )
