# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.views.generic.base import TemplateView

from elements.locations.utils import breadcrumbs_context
from elements.participants.models import EntityParticipant
from elements.utils import clean_html, entity_post_method
from elements.views import entity_base_view
from tools.ideas.models import Idea
from tools.ideas.notification import NewIdeaNotification

class IdeaView(TemplateView):
    template_name = 'ideas/view.html'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(IdeaView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))
        ctx.update(entity_base_view(self, Idea, {'id': id}))

        location = self.entity.task.info()['locations']['entities'][0]['instance']
        ctx.update(breadcrumbs_context(location))

        projects = [pi.project for pi in self.entity.projects.select_related('project')]
        ctx.update({
            'idea': self.entity,
            'admin': self.info['participants']['admin']['entities'][0],
            'projects': projects,
        })
        return ctx

@entity_post_method
def add_idea(request, entity):
    description = request.POST.get('description', '').strip()
    if description == '':
        return HttpResponse(u'Пожалуйста, опишите идею')

    idea = Idea.objects.create(task=entity, description=clean_html(description))

    EntityParticipant.objects.add(idea, request.profile, 'admin')

    # TODO: add resources

    NewIdeaNotification.send(idea.id)

    entity.clear_cache()

    return HttpResponse('ok')
