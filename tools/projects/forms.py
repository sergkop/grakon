# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.locations.forms import location_init
from elements.utils import form_helper
from tools.projects.models import Project

@location_init(False, u'Место')
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

    helper = form_helper('', u'Сохранить')
    helper.layout = Layout(
        Fieldset('', 'title', 'deadline', 'goals', 'about', 'team', 'location_select'),
    )
