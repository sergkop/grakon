# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.models import EntityAdmin, EntityFollower
from elements.utils import table_data
from services.disqus import disqus_page_params
from tools.events.forms import EventForm
from tools.events.models import Event

class BaseEventView(object):
    template_name = 'events/base.html'
    tab = None # 'view' or 'edit'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseEventView, self).get_context_data(**kwargs)
        self.event = get_object_or_404(Event, id=int(self.kwargs.get('event_id')))

        is_admin = False
        is_follower = False
        if self.request.user.is_authenticated():
            is_admin = EntityAdmin.objects.is_admin(self.event, self.request.profile)
            is_follower = EntityFollower.objects.is_followed(self.event, self.request.profile)

        tabs = [
            ('view', u'Информация', self.event.get_absolute_url(), 'events/view.html', 'wall-tab'),
            ('participants', u'Участники', reverse('event_participants', args=[self.event.id]), 'events/participants.html', ''),
        ]

        if is_admin:
            tabs.append(('edit', u'Редактировать', reverse('edit_event', args=[self.event.id]),
                    'events/edit.html', ''))

        self.info = self.event.info()

        ctx.update({
            'tools_menu_item': True,
            'tab': self.tab,
            'tabs': tabs,
            'info': self.info,
            'event': self.event,
            'is_follower': is_follower,
            'is_admin': is_admin,
        })
        ctx.update(self.update_context())
        return ctx

class EventView(BaseEventView, TemplateView):
    tab = 'view'

    def update_context(self):
        return disqus_page_params('event/'+str(self.event.id), self.event.get_absolute_url(), 'events')

class EventParticipantsView(BaseEventView, TemplateView):
    tab = 'participants'

    def update_context(self):
        participants_types = [
            ('admins', u'Организаторы', 'events/admins.html', self.event.get_admins),
            ('followers', u'Следят', 'events/followers.html', self.event.get_followers),
        ]

        p_type = self.request.GET.get('type', '')
        if p_type not in map(lambda p: p[0], participants_types):
            p_type = 'admins'

        name, title, template, method = filter(lambda p: p[0]==p_type, participants_types)[0]

        ctx = table_data(self.request, 'participants', method)

        base_url = reverse('event_participants', args=[self.event.id])
        ctx.update({
            'table_cap_choices': map(lambda p: (base_url+'?type='+p[0], p[1]), participants_types),
            'table_cap_title': title,
            'table_cap_template': template,
        })
        return ctx

# TODO: test that only admin can edit event page
class EditEventView(BaseEventView, UpdateView):
    form_class = EventForm
    tab = 'edit'

    def get_object(self):
        return get_object_or_404(Event, id=int(self.kwargs.get('event_id')))

    def get_success_url(self):
        return reverse('event', args=[self.kwargs.get('event_id')])

# TODO: need more strict condition
edit_event = login_required(EditEventView.as_view())

class CreateEventView(CreateView):
    template_name = 'events/create.html'
    form_class = EventForm
    model = Event

    def form_valid(self, form):
        event = form.save()

        EntityAdmin.objects.add(event, self.request.profile)
        EntityFollower.objects.add(event, self.request.profile)

        response = super(CreateEventView, self).form_valid(form)
        return response

create_event = login_required(CreateEventView.as_view())
