# -*- coding:utf-8 -*-
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from elements.participants.models import EntityParticipant
from services.disqus import disqus_page_params
from tools.ideas.models import Idea

# TODO: use entity_base_view
def idea_view(request, id):
    id = int(id)
    entity = get_object_or_404(Idea, id=id)

    info = entity.info()

    projects = [pi.project for pi in entity.projects.select_related('project')]

    ctx = {
        'info': info,
        'idea': entity,
        'admin': info['participants']['admin']['entities'][0]['instance'],
        'projects': projects,
    }

    # TODO: all data can be recieved in one db query
    for role in Idea.roles:
        if request.user.is_authenticated():
            ctx['is_'+role] = EntityParticipant.objects.is_participant(entity, request.profile, role)
        else:
            ctx['is_'+role] = False

    ctx.update(disqus_page_params('idea/'+str(id), entity.get_absolute_url(), 'ideas'))

    return render_to_response('ideas/view.html', context_instance=RequestContext(request, ctx))
