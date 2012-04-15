# -*- coding:utf-8 -*-
import json

from django import forms
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from crispy_forms.layout import HTML

from locations.models import Location

class LocationSelectWidget(Widget):
    def render(self, name, value, attrs=None):
        """ value is a location path - the list [tegion_id, district_id, location_id] """

        #print "value", value, attrs

        value = value or []

        html = '<div id="%s">%s</div>' % (name, render_to_string('elements/select_location.html'))
        html += '<script type="text/javascript">' \
                    '$().ready(function(){' \
                        '(new SelectLocation({el: $("#%s"), path: %s})).render();' \
                    '});' \
                '</script>' % (name, json.dumps(value))
        html += '<input type="text" name="%s" style="display:none;" value="test" />' % name

        return mark_safe(html)

def location_init(form, required, label):
    """ If required then the lowest possible level must be chosen """
    form.required = required

    form.fields.update({
        'location_select': forms.CharField(label=label, required=True, initial=[],
                widget=LocationSelectWidget),
        'region': forms.CharField(required=False),
        'district': forms.CharField(required=False),
        'location': forms.CharField(required=False),
    })

def form_location_path(form):
    path = []
    if getattr(form, 'location', None):
        for attr in ('region_id', 'district_id', 'id'):
            if getattr(form.location, attr) is not None:
                path.append(getattr(form.location, attr))

    # TODO: pass path to location_select on errors
    #form.fields['location_select'].initial = path
    #form.fields['location_select'].widget.attrs['dat'] = path
    #form.initial['location_select'] = path
    #form.cleaned_data['location_select'] = path
    #print "path", path

def location_clean(form):
    msg = u'Необходимо выбрать нижний уровень географической иерархии'

    try:
        form.location = Location.objects.get(id=int(form.cleaned_data.get('location', '')))
    except (ValueError, Location.DoesNotExist):
        try:
            form.location = Location.objects.get(id=int(form.cleaned_data.get('district', '')))
        except (ValueError, Location.DoesNotExist):
            try:
                form.location = Location.objects.get(id=int(form.cleaned_data.get('region', '')))
            except (ValueError, Location.DoesNotExist):
                if form.required:
                    form_location_path(form)
                    raise forms.ValidationError(msg)
                else:
                    form.location = Location.objects.country()

    if form.required:
        if form.location.region_id is None:
            form_location_path(form)
            raise forms.ValidationError(msg)

        # Check that this is the lowest possible level
        # TODO: doesn't work with 2 level depth (Адыгея->Адыгейск)
        if form.location.is_district():
            if Location.objects.filter(district=form.location).count() == 0:
                form_location_path(form)
                raise forms.ValidationError(msg)

    print form.location
    form_location_path(form)
    return form.cleaned_data
