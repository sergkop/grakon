# -*- coding:utf-8 -*-
import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView

from locations.models import Location
from locations.utils import subregion_list
from users.models import Profile

class BaseLocationView(object):
    template_name = 'locations/base.html'
    tab = None # 'wall', 'map', 'tools', 'participants'

    def update_context(self):
        """ Override in child classes to add context variables """
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseLocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            self.location = location = Location.objects.select_related('region', 'district').get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Район не найден')

        self.info = location.info(related=True) # TODO: use settings.TOP_PARTICIPANTS_COUNT

        tabs = [
            ('wall', u'Стена', reverse('location', args=[location.id]), 'locations/wall.html', ''),
            ('map', u'Карта', reverse('location_map', args=[location.id]), 'locations/map.html', ''),
            ('tools', u'Инструменты', reverse('location_tools', args=[location.id]), 'locations/tools.html', ''),
            ('participants', u'Участники', reverse('location_participants', args=[location.id]), 'locations/participants.html', ''),
        ]

        ctx.update({
            'loc_id': kwargs['loc_id'], # TODO: what is it for?
            'tab': self.tab,
            'tabs': tabs,
            'location': location,
            'subregions': subregion_list(location),
            'info': self.info,
        })

        ctx.update(self.update_context())
        return ctx

class WallLocationView(BaseLocationView, TemplateView):
    tab = 'wall'

class MapLocationView(BaseLocationView, TemplateView):
    tab = 'map'

class ToolsLocationView(BaseLocationView, TemplateView):
    tab = 'tools'

class ParticipantsLocationView(BaseLocationView, TemplateView):
    tab = 'participants'

    def update_context(self):
        try:
            start = int(self.request.GET.get('start', 0))
        except ValueError:
            start = 0

        # TODO: allow to choose limit (?), max allow value of it
        # TODO: accept sorting field

        profile_ids = Profile.objects.for_location(self.location, start, limit=20)['ids']
        participants_info = Profile.objects.info_for(profile_ids, related=False)
        participants = [participants_info[id] for id in profile_ids if id in participants_info]

        ctx = {
            'participants': participants,
        }
        return ctx

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

    url = reverse('location', args=[loc_id])
    return HttpResponseRedirect(url)
