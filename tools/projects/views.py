# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.locations.utils import subregion_list
from elements.participants.models import EntityParticipant
from elements.utils import authenticated_ajax_post
from elements.views import entity_base_view, entity_tabs_view
from services.disqus import disqus_page_params
from tools.ideas.models import Idea
from tools.projects.forms import ProjectForm
from tools.projects.models import Project, ProjectIdeas

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
            ('participants', u'Участники: %i' % self.info['instance'].rating, reverse('project_participants', args=[id]), '', 'projects/participants.html'),
        ]

        ctx.update(entity_tabs_view(self))

        # TODO: select_related it needed (?)
        location = ctx['info']['locations']['entities'][0]['instance'] # TODO: looks hacky

        ctx.update({
            'project': self.entity,
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

@authenticated_ajax_post
def link_idea_to_project(request):
    try:
        project_id = int(request.POST.get('project', ''))
        project = Project.objects.get(id=project_id)
    except ValueError, Project.DoesNotExist:
        return HttpResponse(u'Проект указан неверно')

    if not EntityParticipant.objects.is_participant(project, request.profile, 'admin'):
        return HttpResponse(u'У вас нет прав на добавление идеи')

    try:
        idea_id = int(request.POST.get('idea', ''))
        idea = Idea.objects.get(id=idea_id)
    except ValueError:
        return HttpResponse(u'Идея указана неверно')

    ProjectIdeas.objects.get_or_create(project=project, idea=idea)

    project.clear_cache()
    idea.clear_cache()

    return HttpResponse('ok')
