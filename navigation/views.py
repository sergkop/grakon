from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse

from locations.models import Location
from locations.views import WallLocationView
from navigation.forms import FeedbackForm
from services.cache import cache_view

def main(request):
    country_id = Location.objects.country().id
    return WallLocationView.as_view()(request, loc_id=country_id)

# TODO: how to utilise caching for logged in users?
@cache_view(lambda args, kwargs: 'static_page/'+kwargs['tab'], 60)
def static_page(request, **kwargs):
    """ 
    kwargs must contain the following keys: 'tab', 'template', 'tabs', 'menu_item'.
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
            context_instance=RequestContext(request, {'menu_item': 'help'}))
