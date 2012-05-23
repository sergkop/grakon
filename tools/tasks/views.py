# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.participants.models import EntityParticipant
from elements.utils import table_data
from elements.views import entity_base_view, participants_view
from services.disqus import disqus_page_params
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
        self.participants_url = reverse('task_participants', args=[id])
        ctx.update(entity_base_view(self, Task, id))

        tabs = [
            ('view', u'Информация', self.entity.get_absolute_url(), 'tasks/view.html', ''),
            ('wall', u'Обсуждение', reverse('task_wall', args=[id]), 'disqus/comments.html', 'wall-tab'),
            ('participants', u'Участники', self.participants_url, 'elements/table_tab.html', ''),
        ]

        if ctx['is_admin']:
            tabs.append(('edit', u'Редактировать', reverse('edit_task', args=[id]),
                    'elements/edit_form.html', ''))

        ctx.update({
            'tabs': tabs,
            'task': self.entity,
            'admins_title': u'Админы',
            'follow_button': {
                'cancel_msg': u'Вы хотите отписаться от новостей об этой задаче?',
                'cancel_btn': u'Отписаться',
                'cancel_btn_long': u'Отписаться',
                'confirm_msg': u'Вы хотите следить за новыми идеями для этой задачи?',
                'confirm_btn': u'Следить',
                'confirm_btn_long': u'Следить',
            },
        })
        ctx.update(disqus_page_params('task/'+str(id), reverse('task_wall', args=[id]), 'tasks'))
        return ctx

class TaskView(BaseTaskView, TemplateView):
    tab = 'view'

    def update_context(self):
        return table_data(self.request, 'posts', self.entity.get_posts, 5)

class TaskWallView(BaseTaskView, TemplateView):
    tab = 'wall'

class TaskParticipantsView(BaseTaskView, TemplateView):
    tab = 'participants'

    def update_context(self):
        return participants_view(self)

# TODO: test that only admin can edit task page
class EditTaskView(BaseTaskView, UpdateView):
    form_class = TaskForm
    tab = 'edit'

    def get_object(self):
        return get_object_or_404(Task, id=int(self.kwargs.get('id')))

    def get_success_url(self):
        return reverse('task', args=[self.kwargs.get('id')])

# TODO: need more strict condition
edit_task = login_required(EditTaskView.as_view())

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
