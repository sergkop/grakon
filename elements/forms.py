# -*- coding:utf-8 -*-
import json

from django import forms
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from crispy_forms.layout import HTML

from elements.models import EntityLocation
from elements.utils import class_decorator, clean_html
from locations.models import Location

class HTMLCharField(forms.CharField):
    def clean(self, value):
        html = super(HTMLCharField, self).clean(value)
        return clean_html(html)

class LocationSelectWidget(Widget):
    def render(self, name, value, attrs=None):
        """ value is a location path - the list [region_id, district_id, location_id] """
        value = value or []

        html = '<div id="%s">%s</div>' % (name, render_to_string('elements/select_location.html'))
        html += '<script type="text/javascript">' \
                    '$().ready(function(){' \
                        '(new SelectLocation({el: $("#%s"), path: %s})).render();' \
                    '});' \
                '</script>' % (name, json.dumps(value))
        html += '<input type="text" name="%s" style="display:none;" value="test" />' % name

        return mark_safe(html)

# TODO: write one method taking a list of features (take params from models)
# TODO: rename it
def location_init(required, label):
    """ If required then the lowest possible level must be chosen """
    attrs = {
        'location_select': forms.CharField(label=label, required=True, initial=[],
                widget=LocationSelectWidget),
        'region': forms.CharField(required=False),
        'district': forms.CharField(required=False),
        'location': forms.CharField(required=False),
    }

    def decorator(cls):
        new_cls = class_decorator(attrs)(cls)
        new_cls.Meta.exclude = getattr(new_cls.Meta, 'exclude', ()) + ('region', 'district', 'location')

        clean = new_cls.clean
        def new_clean(form):
            form.cleaned_data = location_clean(form)
            return clean(form)
        new_cls.clean = new_clean

        save = new_cls.save
        def new_save(form):
            entity = save(form)

            # TODO: what about is_main (take decorator params to control it)
            # TODO: it can cause IntegrityError
            EntityLocation.objects.create(entity=entity, location=form.location, is_main=True)

            return entity
        new_cls.save = new_save

        new_cls.required = required

        return new_cls

    return decorator

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
        if form.location.is_district():
            if Location.objects.filter(district=form.location).count() != 0:
                form_location_path(form)
                raise forms.ValidationError(msg)

    form_location_path(form)
    return form.cleaned_data
