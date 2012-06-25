# -*- coding:utf-8 -*-
from django import forms

from elements.locations.models import EntityLocation
from elements.locations.widgets import LocationSelectWidget
from locations.models import Location

class LocationSelectField(forms.CharField):
    # Override this method to recover location path on errors in form
    def bound_data(self, data, initial):
        return initial

# TODO: write one method taking a list of features (take params from models) + classes with methods and data
# TODO: rename it
# TODO: if required is False provide help_text saying that nothing chosen means Russia
def location_init(required, label):
    """ If required then the lowest possible level must be chosen """
    attrs = {
        'location_select': LocationSelectField(label=label, required=required, initial=[],
                widget=LocationSelectWidget),
        'region': forms.CharField(required=False),
        'district': forms.CharField(required=False),
        'location': forms.CharField(required=False),
    }
    if not required:
        attrs['location_select'].help_text = u'если не выбрать место, то задача добавится на страницу России'

    def decorator(cls):
        new_cls = cls.__metaclass__(cls.__name__, (cls,), attrs)
        new_cls.Meta.exclude = getattr(new_cls.Meta, 'exclude', ()) + ('region', 'district', 'location')

        old_init = new_cls.__init__
        def new_init(form, *args, **kwargs):
            old_init(form, *args, **kwargs)
            if form.instance.id: # if this is editing form
                location_info = EntityLocation.objects.get_for(type(form.instance), [form.instance.id])[form.instance.id]
                loc_id = location_info['ids'][0] # TODO: which location to choose?
                form.fields['location_select'].initial = Location.objects.get(id=loc_id).path()
        new_cls.__init__ = new_init

        clean = new_cls.clean
        def new_clean(form):
            form.cleaned_data = location_clean(form)
            return clean(form)
        new_cls.clean = new_clean

        # TODO: location_init should take parameter, which controls whether location is added or updated
        save = new_cls.save
        def new_save(form):
            is_create_form = form.instance.id is None

            entity = save(form)

            # TODO: what about is_main (take decorator params to control it)
            if is_create_form:
                EntityLocation.objects.add(entity, form.location, params={'is_main': True})
            else:
                EntityLocation.objects.update_location(entity, form.location)

            return entity
        new_cls.save = new_save

        new_cls.required = required

        return new_cls

    return decorator

def form_location_path(form):
    form.initial['location_select'] = []
    if getattr(form, 'location', None):
        form.initial['location_select'] = form.location.path()

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
