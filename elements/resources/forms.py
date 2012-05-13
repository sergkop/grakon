# -*- coding:utf-8 -*-
from django import forms

from elements.resources.models import EntityResource, RESOURCE_CHOICES
from elements.resources.widgets import ResourcesSelectWidget

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
