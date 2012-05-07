# -*- coding:utf-8 -*-
from django import forms

from elements.models import EntityLocation, EntityResource, RESOURCE_CHOICES
from elements.utils import clean_html
from elements.widgets import LocationSelectWidget, ResourcesSelectWidget
from locations.models import Location

class HTMLCharField(forms.CharField):
    def clean(self, value):
        html = super(HTMLCharField, self).clean(value)
        return clean_html(html)

# TODO: write one method taking a list of features (take params from models) + classes with methods and data
# TODO: rename it
# TODO: if required is False provide help_text saying that nothing chosen means Russia
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
        new_cls = cls.__metaclass__(cls.__name__, (cls,), attrs)
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
            EntityLocation.objects.add(entity, form.location, params={'is_main': True})

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

    if form.required and not form.location.is_lowest_level():
        form_location_path(form)
        raise forms.ValidationError(msg)

    form_location_path(form)
    return form.cleaned_data

def resources_init(cls):
    # TODO: take resources label as an argument (and description)
    attrs = {'resources1': forms.MultipleChoiceField(label=u'Навыки и ресурсы',
            choices=RESOURCE_CHOICES, widget=ResourcesSelectWidget,
            help_text=u'Можно выбрать несколько')}
    new_cls = cls.__metaclass__(cls.__name__, (cls,), attrs)

    old_init = new_cls.__init__
    def new_init(form, *args, **kwargs):
        old_init(form, *args, **kwargs)
        if form.instance.id: # if this is editing form
            form.fields['resources1'].initial = map(lambda er: er['name'],
                    EntityResource.objects.get_for(type(form.instance), [form.instance.id])[form.instance.id])
    new_cls.__init__ = new_init

    save = new_cls.save
    def new_save(form):
        entity = save(form)
        entity.update_resources(form.cleaned_data['resources1'])
        return entity
    new_cls.save = new_save

    return new_cls

"""
def image_init(cls):
    attrs = {
        'photo': forms.FileField(label=u'Фотография', help_text=u'Размер не должен превышать 5 Мб')
    }

    new_cls = cls.__metaclass__(cls.__name__, (cls,), attrs)

    save = new_cls.save
    def new_save(form):
        entity = save(form)

        return entity
    new_cls.save = new_save

    return new_cls
"""
