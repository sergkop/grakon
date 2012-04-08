# -*- coding:utf-8 -*-
from django.views.generic.base import TemplateView

from locations.models import Location
from services.cache import cache_function

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



def get_subregions(request):
    if not request.is_ajax():
        return HttpResponse('[]')

    try:
        loc_id = int(request.GET.get('loc_id', ''))
    except ValueError:
        return HttpResponse('[]')

    try:
        location = Location.objects.get(id=loc_id)
    except Location.DoesNotExist:
        return HttpResponse('[]')

    if location.district: # 4th level location (no children)
        return HttpResponse('[]')
    elif location.region: # 3rd level location (district)
        res = []
        for loc in Location.objects.filter(tik=location).order_by('name'):
            res.append({'name': loc.name, 'id': loc.id})
        return HttpResponse(json.dumps(res))
    else: # 1st level location
        res = []
        for loc in Location.objects.filter(region=location, tik=None).order_by('name'):
            res.append({'name': loc.name, 'id': loc.id})
        return HttpResponse(json.dumps(res))

@cache_function(lambda args, kwargs: 'subregions/'+args[0].id, 500)
def subregion_list(location=None):
    """ location=None for country """
    if location is None:
        res = [('', u'Выбрать субъект РФ'), None, None] # reserve places for Moscow, St. Petersburg and foreign countries
        for loc_id, name in Location.objects.filter(region=None).order_by('name').values_list('id', 'name'):
            if name == u'Москва':
                regions[1] = (loc_id, name)
            elif name == u'Санкт-Петербург':
                regions[2] = (loc_id, name)
            #elif name == FOREIGN_TERRITORIES:
            #    regions[3] = (loc_id, name)
            else:
                regions.append((loc_id, name))
        return regions
    elif location.is_region():
        return list(Location.objects.filter(region=location, tik=None).order_by('name').values_list('id', 'name'))
    elif location.is_tik():
        return list(Location.objects.filter(tik=location).order_by('name').values_list('id', 'name'))
    else:
        return []