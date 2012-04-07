# -*- coding:utf-8 -*-
from django.views.generic.base import TemplateView

from locations.models import Location

class LocationView(TemplateView):
    template_name = 'locations/base.html'

    def update_context(self):
        """ Override in child classes to add context variables """
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(LocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            self.location = location = Location.objects.select_related().get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Район не найден')

        tab = self.request.GET.get('tab', '')
        if tab not in ('wall', 'map'):
            tab = 'wall'

        # TODO: automate generating it + move it to class attributes (?)
        tabs = [
            ('wall', u'Стена', location.get_absolute_url()+'?tab=wall', 'locations/wall.html', ''),
            ('map', u'Карта', location.get_absolute_url()+'?tab=map', 'locations/map.html', ''),
        ]

        ctx.update({
            'loc_id': kwargs['loc_id'],
            'tab': tab,
            'tabs': tabs,
            'location': location,
        })

        ctx.update(self.update_context())
        return ctx
