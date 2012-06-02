# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.participants.models import EntityParticipant
from elements.views import entity_base_view, participants_view
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

        id = int(self.kwargs.get('id'))
        self.participants_url = reverse('event_participants', args=[id])
        ctx.update(entity_base_view(self, Event, id))

        tabs = [
            ('view', u'Информация', self.entity.get_absolute_url(), 'events/view.html', 'wall-tab'),
            ('participants', u'Участники', self.participants_url, 'elements/table_tab.html', ''),
        ]

        if ctx['is_admin']:
            tabs.append(('edit', u'Редактировать', reverse('edit_event', args=[id]),
                    'elements/edit_form.html', ''))

        ctx.update({
            'tabs': tabs,
            'event': self.entity,
            'follow_button': {
                'cancel_msg': u'Вы хотите отписаться от новостей об этом мероприятии?',
                'cancel_btn': u'Отписаться',
                'cancel_btn_long': u'Отписаться',
                'confirm_msg': u'Вы хотите следить за новостями об этом мероприятии?',
                'confirm_btn': u'Следить',
                'confirm_btn_long': u'Следить',
            },
        })
        ctx.update(disqus_page_params('event/'+str(id), self.entity.get_absolute_url(), 'events'))
        return ctx

class EventView(BaseEventView, TemplateView):
    tab = 'view'

class EventParticipantsView(BaseEventView, TemplateView):
    tab = 'participants'

    def update_context(self):
        return participants_view(self)

# TODO: test that only admin can edit event page
class EditEventView(BaseEventView, UpdateView):
    form_class = EventForm
    tab = 'edit'

    def get_object(self):
        return get_object_or_404(Event, id=int(self.kwargs.get('id')))

    def get_success_url(self):
        return reverse('event', args=[self.kwargs.get('id')])

# TODO: need more strict condition
edit_event = login_required(EditEventView.as_view())

class CreateEventView(CreateView):
    template_name = 'events/create.html'
    form_class = EventForm
    model = Event

    def form_valid(self, form):
        event = form.save()

        for role in ('admin', 'follower', 'participant'):
            EntityParticipant.objects.add(event, self.request.profile, role)

        response = super(CreateEventView, self).form_valid(form)
        return response

create_event = login_required(CreateEventView.as_view())
