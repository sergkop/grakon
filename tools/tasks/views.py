# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.locations.utils import subregion_list
from elements.participants.models import EntityParticipant
from elements.views import entity_base_view, entity_tabs_view
from services.disqus import disqus_page_params
from tools.ideas.models import Idea
from tools.tasks.forms import TaskForm
from tools.tasks.models import Task

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
        location = ctx['info']['locations']['entities'][0]['location'] # TODO: looks hacky

        ctx.update({
            'task': self.entity,
            'follow_button': {
                'cancel_msg': u'Вы хотите отписаться от новостей об этой задаче?',
                'cancel_btn': u'Отписаться',
                'cancel_btn_long': u'Отписаться',
                'confirm_msg': u'Вы хотите следить за новыми идеями для этой задачи?',
                'confirm_btn': u'Следить',
                'confirm_btn_long': u'Следить',
            },
            'location': location,
            'subregions': subregion_list(location),

            # TODO: fix it
            'admin': ctx['info']['participants']['admin']['entities'][0]['instance'],
        })
        ctx.update(disqus_page_params('task/'+str(id), reverse('task_wall', args=[id]), 'tasks'))
        return ctx

class TaskView(BaseTaskView, TemplateView):
    tab = 'view'

    def update_context(self):
        ideas_ids = list(self.entity.ideas.all().values_list('id', flat=True))
        ideas = Idea.objects.info_for(ideas_ids, True).values()

        ctx = {
            'ideas': ideas,
            'template_path': 'tasks/view.html',
        }
        return ctx

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
