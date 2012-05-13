# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.layout import Fieldset, Layout

from elements.locations.forms import location_init
from elements.utils import form_helper
from elements.widgets import DateTimeWidget
from tools.events.models import Event

@location_init(False, u'Место проведения')
class EventForm(forms.ModelForm):
    event_time = forms.DateTimeField(label=u'Время проведения', input_formats=['%d/%m/%Y %H:%M'],
            widget=DateTimeWidget(format='%d/%m/%Y %H:%M'))

    class Meta:
        model = Event

    helper = form_helper('', u'Сохранить')
    helper.layout = Layout(
        Fieldset('', 'title', 'location_select', 'place', 'event_time', 'description'),
    )
