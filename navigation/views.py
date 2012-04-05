from django.shortcuts import render_to_response
from django.template import RequestContext

from services.cache import cache_view

def main(request):
    ctx = {}
    return render_to_response("main/base.html", context_instance=RequestContext(request, ctx))

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
