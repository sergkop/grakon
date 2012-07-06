# -*- coding:utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView

from elements.locations.utils import breadcrumbs_context, subregion_list
from elements.models import ENTITIES_MODELS
from elements.participants.models import EntityParticipant
from elements.utils import table_data
from elements.views import entity_tabs_view
from locations.models import Location

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

        # TODO: take it from cache (should be in location info)
        tasks_count = location.get_entities('tasks')(limit=0)['count']
        projects_count = location.get_entities('projects')(limit=0)['count']

        self.tabs = [
            #('map', u'Карта', reverse('location_map', args=[location.id]), '', 'locations/map.html'),
            ('tasks', u'Задачи: %i' % tasks_count, reverse('location_tasks', args=[location.id]), '', 'tasks/list.html'),
            ('projects', u'Проекты: %i' % projects_count, reverse('location_projects', args=[location.id]), '', 'projects/list.html'),
            ('wall', u'Комментарии: %i' % self.info['comments']['count'], reverse('location_wall', args=[location.id]), '', 'locations/wall.html'),
            ('participants', u'Участники: %i' % self.info['participants']['count'], reverse('location_participants', args=[location.id]), '', 'locations/participants.html'),
        ]

        ctx.update(entity_tabs_view(self))
        ctx.update(breadcrumbs_context(location))

        ctx.update({
            'title': location.name,
            'loc_id': kwargs['loc_id'], # TODO: what is it for?
            'info': self.info,
            'is_participant': self.request.user.is_authenticated() and \
                    location.id in self.request.profile_info['locations']['ids'],
            'is_lowest_level': location.is_lowest_level(),
            'is_location_page': True,
        })
        ctx.update(self.update_context())
        return ctx

class LocationTasksView(BaseLocationView, TemplateView):
    tab = 'tasks'

    def update_context(self):
        return table_data(self.request, 'tasks', self.location.get_entities('tasks'))

class LocationProjectsView(BaseLocationView, TemplateView):
    tab = 'projects'

    def update_context(self):
        return table_data(self.request, 'projects', self.location.get_entities('projects'))

class LocationWallView(BaseLocationView, TemplateView):
    tab = 'wall'

#class MapLocationView(BaseLocationView, TemplateView):
#    tab = 'map'

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

    url = reverse('location_tasks', args=[loc_id])
    return HttpResponseRedirect(url)
