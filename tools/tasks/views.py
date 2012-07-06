# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.locations.utils import breadcrumbs_context
from elements.participants.models import EntityParticipant
from elements.resources.models import RESOURCE_CHOICES
from elements.views import entity_base_view, entity_tabs_view
from tools.ideas.models import Idea
from tools.tasks.forms import TaskForm
from tools.tasks.models import Task
from users.models import Profile

class BaseTaskView(object):
    template_name = 'tasks/base.html'
    tab = None

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseTaskView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))

        ctx.update(entity_base_view(self, Task, {'id': id}))

        # Get (unique) supporters
        supporters_by_id = {}
        for idea_info in self.info['ideas']['entities']:
            for provider_id in idea_info['resources']:
                supporters_by_id[provider_id] = idea_info['resources'][provider_id]['provider']

        # Get (unique) idea admins
        idea_admins_by_id = {}
        for idea_info in self.info['ideas']['entities']:
            for idea_admin in idea_info['participants']['admin']['entities']:
                idea_admins_by_id[idea_admin['id']] = idea_admin

        # TODO: select_related it needed
        location = ctx['info']['locations']['entities'][0]['instance'] # TODO: looks hacky
        ctx.update(breadcrumbs_context(location))

        ctx.update({
            'title': u'Задача: '+self.entity.title,
            'task': self.entity,

            # TODO: fix it
            'admin': ctx['info']['participants']['admin']['entities'][0],

            'supporters': supporters_by_id.values(),
            'idea_admins': idea_admins_by_id.values(),

            'RESOURCE_CHOICES': RESOURCE_CHOICES, # TODO: use idea form instead
        })
        return ctx

class TaskView(BaseTaskView, TemplateView):
    tab = 'view'

    def update_context(self):
        ideas = Idea.objects.info_for(self.info['ideas']['ids'], True).values()
        return {
            'ideas': sorted(ideas, key=lambda info: -len(info['resources'])),
            'template_path': 'tasks/view.html',
        }

class CreateTaskView(CreateView):
    template_name = 'tasks/create.html'
    form_class = TaskForm
    model = Task

    def form_valid(self, form):
        task = form.save()

        EntityParticipant.objects.add(task, self.request.profile, 'admin')
        EntityParticipant.objects.add(task, self.request.profile, 'follower')

        response = super(CreateTaskView, self).form_valid(form)
        return response

create_task = login_required(CreateTaskView.as_view())
