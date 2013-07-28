# -*- coding:utf-8 -*-
from django.conf import settings
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from elements.locations.utils import breadcrumbs_context
from elements.models import ENTITIES_MODELS
from elements.resources.models import RESOURCE_DICT
from locations.models import Location
from navigation.forms import FeedbackForm

def main(request):
    country = Location.objects.country()

    #if request.user.is_authenticated():
    return redirect(country.get_absolute_url())

    data = {}
    for entity_type in ('tasks', 'ideas', 'projects'):
        ids = ENTITIES_MODELS[entity_type].objects.order_by('-rating').values_list('id', flat=True)[:3]
        entities_info =  ENTITIES_MODELS[entity_type].objects.info_for(ids, related=False)
        data[entity_type] = [entities_info[id] for id in ids]

    ctx = {
        'title': u'Соцсеть гражданских активистов',
        'description': settings.SLOGAN,
        'is_main': True,
        'country_url': country.get_absolute_url(),
        'lists_data': data,
        'RESOURCE_DICT': RESOURCE_DICT,
    }
    return render_to_response('main.html', context_instance=RequestContext(request, ctx))

# TODO: how to utilise caching for logged in users?
#@cache_view(lambda args, kwargs: 'static_page/'+kwargs['tab'], 60)
def static_page(request, **kwargs):
    """ 
    kwargs must contain the following keys: 'tab', 'template', 'tabs'.
    kwargs['tabs']=[(name, url, template, css_class), ...]
    """
    ctx = breadcrumbs_context(Location.objects.country())
    ctx.update(kwargs)
    return render_to_response(kwargs['template'], context_instance=RequestContext(request, ctx))

def feedback(request, **kwargs):
    if request.method == 'POST':
        form = FeedbackForm(request, request.POST)
        if form.is_valid():
            form.send()
            return redirect('feedback_thanks')
    else:
        form = FeedbackForm(request)

    ctx = {
        'form': form,
        'template': 'feedback/feedback.html',
    }
    ctx.update(kwargs)
    return static_page(request, **ctx)
