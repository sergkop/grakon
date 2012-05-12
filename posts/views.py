from django.http import HttpResponse
from django.views.generic.base import TemplateView

from elements.utils import entity_post_method
from grakon.utils import escape_html
from posts.models import EntityPost

class PostView(TemplateView):
    pass

# TODO: limit the number of symbols
@entity_post_method
def add_post(request, entity):
    EntityPost.objects.add(entity, request.profile, escape_html(request.POST.get('content', '')),
            request.POST.get('url', ''), request.POST.get('opinion', ''))
    return HttpResponse('ok')
