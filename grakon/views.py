import json

from django.shortcuts import render_to_response

from elements.models import RESOURCE_CHOICES

# TODO: cache it
def code_data(request):
    ctx = {
        'resources': json.dumps(RESOURCE_CHOICES, ensure_ascii=False),
    }
    return render_to_response('code_data.js', ctx, mimetype='application/javascript')
