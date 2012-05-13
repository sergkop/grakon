import json
import os.path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response

from elements.resources.models import RESOURCE_CHOICES
from services.cache import cache_view

def code_data(request):
    ctx = {
        'resources': json.dumps(RESOURCE_CHOICES, ensure_ascii=False),
    }
    return render_to_response('code_data.js', ctx, mimetype='application/javascript')

@cache_view('1x1image', 1000, only_anonym=False)
def img1x1(request):
    data = open(os.path.join(settings.PROJECT_PATH, 'grakon', 'static', 'images', 'letters', '1x1.gif')).read()
    response = HttpResponse(data, mimetype='image/gif')
    response['Cache-Control'] = 'no-cache'
    return response
