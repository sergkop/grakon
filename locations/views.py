# -*- coding:utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView

from elements.locations.utils import subregion_list
from elements.models import ENTITIES_MODELS
from elements.participants.models import EntityParticipant, participant_in
from elements.utils import table_data
from elements.views import entity_tabs_view
from locations.models import Location
from services.disqus import disqus_page_params

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
            #('tools', u'Инструменты', self.tools_url, '', 'locations/tools.html'),
            ('tasks', u'Задачи: %i' % tasks_count, reverse('location_tasks', args=[location.id]), '', 'tasks/list.html'),
            ('projects', u'Проекты: %i' % projects_count, reverse('location_projects', args=[location.id]), '', 'projects/list.html'),
            ('wall', u'Комментарии:', reverse('location_wall', args=[location.id]), 'wall-tab', 'locations/wall.html'),
            ('participants', u'Участники: %i' % self.info['participants']['count'], reverse('location_participants', args=[location.id]), '', 'locations/participants.html'),
        ]

        ctx.update(entity_tabs_view(self))

        if self.request.user.is_authenticated():
            ctx['is_follower'] = EntityParticipant.objects.is_participant(self.location, self.request.profile, 'follower')
        else:
            ctx['is_follower'] = False

        ctx.update({
            'loc_id': kwargs['loc_id'], # TODO: what is it for?
            'location': location,
            'subregions': subregion_list(location),
            'info': self.info,
            'is_participant': self.request.user.is_authenticated() and \
                    location.id in self.request.profile_info['locations']['ids'],
            'is_lowest_level': location.is_lowest_level(),
            'follow_button': {
                'cancel_msg': u'Вы хотите отписаться от новостей об этом проекте?',
                'cancel_btn': u'Отписаться',
                'cancel_btn_long': u'Отписаться',
                'confirm_msg': u'Вы хотите стать участником в этом районе?',
                'confirm_btn': u'Участвовать',
                'confirm_btn_long': u'Стать участником',
                'btn_class': 'gr-follow-button gr-follow-button-blue',
            },
        })
        ctx.update(self.update_context())
        ctx.update(disqus_page_params('loc/'+str(loc_id), reverse('location_wall', args=[location.id]), 'locations'))
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

#class ToolsLocationView(BaseLocationView, TemplateView):
#    tab = 'tools'
#
#    def update_context(self):
#        entity_types = sorted(set(ENTITIES_MODELS.keys()) - set(['participants', 'posts']),
#                key=lambda em: ENTITIES_MODELS[em].entity_title)
#
#        entity_type = self.request.GET.get('type', '')
#        if entity_type not in entity_types:
#            entity_type = 'officials'
#
#        ctx = table_data(self.request, entity_type, self.location.get_entities(entity_type))
#        ctx.update({
#            'table_cap_choices': map(lambda em: (self.tools_url+'?type='+em, ENTITIES_MODELS[em].entity_title), entity_types),
#            'table_cap_title': ENTITIES_MODELS[entity_type].entity_title,
#            'table_cap_template': ENTITIES_MODELS[entity_type].table_cap,
#        })
#        return ctx

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
