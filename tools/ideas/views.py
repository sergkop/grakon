# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.views.generic.base import TemplateView

from elements.participants.models import EntityParticipant
from elements.utils import clean_html, entity_post_method
from elements.views import entity_base_view
from services.disqus import disqus_page_params
from tools.ideas.forms import IdeaForm
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

@entity_post_method
def add_idea(request, entity):
    form = IdeaForm(request.POST)
    if not form.is_valid():
        return HttpResponse('Форма заполнена неверно')

    idea = Idea.objects.create(task=entity, title=form.cleaned_data['title'],
            description=clean_html(form.cleaned_data['description']))

    EntityParticipant.objects.add(idea, request.profile, 'admin')

    # TODO: add resources

    entity.clear_cache()

    return HttpResponse('ok')
