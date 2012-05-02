from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.edit import FormView

from locations.models import Location
from locations.views import WallLocationView
from navigation.forms import FeedbackForm
from services.cache import cache_view

def main(request):
    country_id = Location.objects.country().id
    return WallLocationView.as_view()(request, loc_id=country_id)

# TODO: how to utilise caching for logged in users?
@cache_view(lambda args, kwargs: 'static_page/'+kwargs['tab'], 60)
def static_page(request, tab, template, tabs=[]):
    """ tabs=[(name, url, template, css_class), ...] """
    ctx = {
        'about_menu_item': True,
        'tab': tab,
        'template': template,
        'tabs': tabs,
    }
    return render_to_response(template, context_instance=RequestContext(request, ctx))

class Feedback(FormView):
    form_class = FeedbackForm
    template_name = 'static_pages/how_to_help/base.html'

    def get_context_data(self, **kwargs):
        ctx = super(Feedback, self).get_context_data(**kwargs)
        print 'ctx', ctx
        ctx.update({'tab': 'feedback'})
        return ctx

    def get_form_kwargs(self):
        kwargs = super(Feedback, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        form.send()
        return redirect('feedback_thanks')

feedback = Feedback.as_view()
