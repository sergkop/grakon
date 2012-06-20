# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.locations.utils import subregion_list
from elements.participants.models import EntityParticipant
from elements.resources.models import RESOURCE_CHOICES
from elements.views import entity_base_view, entity_tabs_view
from services.disqus import disqus_page_params
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

        #self.tabs = [
        #    ('view', u'Идеи', reverse('task', args=[id]), '', 'tasks/view.html'),
        #    ('wall', u'Обсуждение', reverse('task_wall', args=[id]), 'wall-tab', 'disqus/comments.html'),
        #]

        #ctx.update(entity_tabs_view(self))

        # TODO: select_related it needed
        location = ctx['info']['locations']['entities'][0]['instance'] # TODO: looks hacky

        supporters_ids = set(provider_id for idea_info in self.info['ideas']['entities'] for provider_id in idea_info['resources'])
        supporters_info = Profile.objects.info_for(supporters_ids, related=False)

        idea_admins_ids = set([idea_admin_id for idea_info in self.info['ideas']['entities'] for idea_admin_id in idea_info['participants']['admin']['ids']])
        idea_admins_info = Profile.objects.info_for(idea_admins_ids, related=False)

        ctx.update({
            'task': self.entity,
            'location': location,
            'subregions': subregion_list(location),

            # TODO: fix it
            'admin': ctx['info']['participants']['admin']['entities'][0]['instance'],

            'supporters': [supporters_info[supporter_ids] for supporter_ids in supporters_ids],
            'idea_admins': [idea_admins_info[idea_admin_ids] for idea_admin_ids in idea_admins_ids],

            'RESOURCE_CHOICES': RESOURCE_CHOICES, # TODO: use idea form instead
        })
        ctx.update(disqus_page_params('task/'+str(id), reverse('task_wall', args=[id]), 'tasks'))
        return ctx

class TaskView(BaseTaskView, TemplateView):
    tab = 'view'

    def update_context(self):
        ideas = Idea.objects.info_for(self.info['ideas']['ids'], True).values()
        return {
            'ideas': sorted(ideas, key=lambda info: -len(info['resources'])),
            'template_path': 'tasks/view.html',
        }

class TaskWallView(BaseTaskView, TemplateView):
    tab = 'wall'

    def update_context(self):
        return {'template_path': 'disqus/comments.html'}

#class TaskParticipantsView(BaseTaskView, TemplateView):
#    tab = 'participants'

#    def update_context(self):
#        return participants_view(self)

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
