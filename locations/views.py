# -*- coding:utf-8 -*-
from django.views.generic.base import TemplateView

from locations.models import Location

class LocationView(TemplateView):
    template_name = 'locations/base.html'

    def update_context(self):
        """ Override in child classed to add context variables """
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(LocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            self.location = location = Location.objects.select_related().get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Район не найден')

        view = self.request.GET.get('view', '')
        # TODO: add list of view types (as class variable)
        
            
        ctx.update({
            'loc_id': kwargs['loc_id'],
            'view': view,
            'location': location,
        })

        ctx.update(self.update_context())
        return ctx
