import json
import os.path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response

from elements.resources.models import RESOURCE_CHOICES
from elements.templatetags.elements import comments_templates, get_mustache_template
from grakon.utils import project_settings
from services.cache import cache_view

def code_data(request):
    ctx = {
        'resources': json.dumps(RESOURCE_CHOICES, ensure_ascii=False),
    }
    ctx.update(project_settings())

    # Include mustache templates
    partials = {}
    for name, path in comments_templates.iteritems():
        partials[name] = get_mustache_template(path)

    ctx['mustache_partials'] = json.dumps(partials, ensure_ascii=False).replace('\\n', ' ')

    return render_to_response('code_data.js', ctx, mimetype='application/javascript')

@cache_view('1x1image', 1000, only_anonym=False)
def img1x1(request):
    data = open(os.path.join(settings.PROJECT_PATH, 'grakon', 'static', 'images', 'letters', '1x1.gif')).read()
    response = HttpResponse(data, mimetype='image/gif')
    response['Cache-Control'] = 'no-cache'
    return response
