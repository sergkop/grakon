# -*- coding:utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView

from elements.models import ENTITIES_MODELS
from elements.utils import disqus_page_params, table_data
from locations.models import Location
from locations.utils import subregion_list

class BaseLocationView(object):
    template_name = 'locations/base.html'
    tab = None # 'wall', 'map', 'tools', 'participants'

    def update_context(self):
        """ Override in child classes to add context variables """
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseLocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        # TODO: do we need select_related? (can we use location from cache?)
        try:
            location = Location.objects.select_related('region', 'district').get(id=loc_id)
        except: # Location.DoesNotExist: # TODO: hack to overcome strange bug
            raise Http404(u'Район не найден')

        self.location = location

        self.info = location.info(related=True)

        tabs = [
            ('wall', u'Стена', reverse('location_wall', args=[location.id]), 'locations/wall.html', 'wall-tab'),
            #('map', u'Карта', reverse('location_map', args=[location.id]), 'locations/map.html', ''),
            ('tools', u'Инструменты', reverse('location_tools', args=[location.id]), 'locations/tools.html', ''),
            ('participants', u'Участники', reverse('location_participants', args=[location.id]), 'locations/participants.html', ''),
        ]

        if location.is_country():
            tabs = [('main', u'Добро пожаловать', reverse('main'), 'main/base.html', '')] + tabs

        ctx.update({
            'menu_item': 'geography',
            'loc_id': kwargs['loc_id'], # TODO: what is it for?
            'tab': self.tab,
            'tabs': tabs,
            'location': location,
            'subregions': subregion_list(location),
            'info': self.info,
            'is_participant': self.request.user.is_authenticated() and \
                    location.id in self.request.profile_info['locations']['ids'],
            'is_lowest_level': location.is_lowest_level(),
        })
        ctx.update(self.update_context())
        ctx.update(disqus_page_params('loc/'+str(loc_id), location.get_absolute_url(), 'locations'))
        return ctx

class WallLocationView(BaseLocationView, TemplateView):
    tab = 'wall'

class MapLocationView(BaseLocationView, TemplateView):
    tab = 'map'

class ToolsLocationView(BaseLocationView, TemplateView):
    tab = 'tools'

    def update_context(self):
        entity_type = self.request.GET.get('type', '')
        if entity_type not in ENTITIES_MODELS.keys() or entity_type=='participants':
            entity_type = 'officials'

        return table_data(self.request, entity_type, self.location.get_entities(entity_type))

class ParticipantsLocationView(BaseLocationView, TemplateView):
    tab = 'participants'

    def update_context(self):
        return table_data(self.request, 'participants', self.location.get_entities('participants'))

def get_subregions(request):
    if not request.is_ajax():
        return HttpResponse('[]')

    loc_id = request.GET.get('loc_id', '')

    if loc_id:
        try:
            location = Location.objects.get(id=int(loc_id))
        except ValueError, Location.DoesNotExist:
            return HttpResponse('[]')
    else:
        location = None

    return HttpResponse(json.dumps(subregion_list(location), ensure_ascii=False))

# TODO: take tab as a parameter
def goto_location(request):
    loc_id = request.GET.get('loc_id', '')

    try:
        int(loc_id)
    except ValueError:
        return HttpResponseRedirect(reverse('main')) # TODO: redirect to country page?

    url = reverse('location_wall', args=[loc_id])
    return HttpResponseRedirect(url)
