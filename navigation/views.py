from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView

from elements.models import ENTITIES_MODELS
from elements.resources.models import RESOURCE_DICT
from locations.models import Location
from locations.views import BaseLocationView
from navigation.forms import FeedbackForm
from services.cache import cache_view

def main(request):
    country = Location.objects.country()

    if request.user.is_authenticated():
        return redirect(country.get_absolute_url())

    data = {}
    for entity_type in ('tasks', 'ideas', 'projects'):
        ids = ENTITIES_MODELS[entity_type].objects.order_by('-rating').values_list('id', flat=True)[:3]
        entities_info =  ENTITIES_MODELS[entity_type].objects.info_for(ids, related=False)
        data[entity_type] = [entities_info[id] for id in ids]

    ctx = {
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
    return render_to_response(kwargs['template'], context_instance=RequestContext(request, kwargs))

def feedback(request, **kwargs):
    if request.method == 'POST':
        form = FeedbackForm(request, request.POST)
        if form.is_valid():
            form.send()
            return redirect('feedback_thanks')
    else:
        form = FeedbackForm(request)

    ctx = {'form': form}
    ctx.update(kwargs)
    return TemplateResponse(request, 'static_pages/how_to_help/base.html', ctx)

def feedback_thanks(request):
    return render_to_response('feedback/thanks.html',
            context_instance=RequestContext(request, {}))
