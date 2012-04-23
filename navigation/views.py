from django.shortcuts import render_to_response
from django.template import RequestContext

from locations.views import LocationView
from services.cache import cache_view

def main(request):
    return LocationView.as_view()(request, loc_id=1)

# TODO: how to utilise caching for logged in users?
@cache_view(lambda args, kwargs: 'static_page/'+kwargs['tab'], 60)
def static_page(request, tab, template, tabs=[]):
    """ tabs=[(name, url, template, css_class), ...] """
    ctx = {
        'tab': tab,
        'template': template,
        'tabs': tabs,
    }
    return render_to_response(template, context_instance=RequestContext(request, ctx))
