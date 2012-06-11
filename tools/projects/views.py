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
from tools.projects.forms import ProjectForm
from tools.projects.models import Project

class BaseProjectView(object):
    template_name = 'projects/base.html'
    tab = None

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseProjectView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))

        ctx.update(entity_base_view(self, Project, {'id': id}))

        self.tabs = [
            ('view', u'Описание', reverse('project', args=[id]), '', 'projects/view.html'),
            ('wall', u'Комментарии:', reverse('project_wall', args=[id]), 'wall-tab', 'disqus/comments.html'),
            ('participants', u'Участники', reverse('project_participants', args=[id]), '', 'projects/participants.html'),
        ]

        ctx.update(entity_tabs_view(self))

        # TODO: select_related it needed (?)
        location = ctx['info']['locations']['entities'][0]['instance'] # TODO: looks hacky

        ctx.update({
            'project': self.entity,
            'follow_button': {
                'cancel_msg': u'Вы хотите отписаться от новостей об этом проекте?',
                'cancel_btn': u'Отписаться',
                'cancel_btn_long': u'Отписаться',
                'confirm_msg': u'Вы хотите следить за этим проектом?',
                'confirm_btn': u'Следить',
                'confirm_btn_long': u'Следить за проектом',
                'btn_class': 'gr-follow-button',
            },
            'location': location,
            'subregions': subregion_list(location),

            # TODO: fix it
            'admin': ctx['info']['participants']['admin']['entities'][0]['instance'],
        })
        ctx.update(disqus_page_params('project/'+str(id), reverse('project_wall', args=[id]), 'projects'))
        return ctx

class ProjectView(BaseProjectView, TemplateView):
    tab = 'view'

    def update_context(self):
        return {
            'ideas': [pi.idea for pi in self.entity.ideas.select_related('idea')],
        }

class ProjectWallView(BaseProjectView, TemplateView):
    tab = 'wall'

class ProjectParticipantsView(BaseProjectView, TemplateView):
    tab = 'participants'

    def update_context(self):
        return {}

class CreateProjectView(CreateView):
    template_name = 'projects/create.html'
    form_class = ProjectForm
    model = Project

    def form_valid(self, form):
        project = form.save()

        EntityParticipant.objects.add(project, self.request.profile, 'admin')
        EntityParticipant.objects.add(project, self.request.profile, 'follower')

        response = super(CreateProjectView, self).form_valid(form)
        return response

create_project = login_required(CreateProjectView.as_view())
