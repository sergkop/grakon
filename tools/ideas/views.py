# -*- coding:utf-8 -*-
from django.views.generic.base import TemplateView

from elements.views import entity_base_view
from services.disqus import disqus_page_params
from tools.ideas.models import Idea

class IdeaView(TemplateView):
    template_name = 'ideas/view.html'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(IdeaView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))
        ctx.update(entity_base_view(self, Idea, {'id': id}))

        projects = [pi.project for pi in self.entity.projects.select_related('project')]
        ctx.update({
            'idea': self.entity,
            'admin': self.info['participants']['admin']['entities'][0]['instance'],
            'projects': projects,
        })
        ctx.update(disqus_page_params('idea/'+str(id), self.entity.get_absolute_url(), 'ideas'))
        return ctx
