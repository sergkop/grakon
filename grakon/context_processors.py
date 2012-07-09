# -*- coding:utf-8 -*-
import json
from urllib import quote

from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.widgets import Media

from grakon.utils import project_settings

# TODO: add IE-specific styles here
# TODO: take extra media files from request - ability to add them per-view (variable in class-based views?)
# TODO: cache it or part of template
def media_files(request):
    media = Media()
    media.add_css({
        'all': (
            'libs/yaml/base.css',
            'libs/jquery-ui/jquery-ui.css',
            'libs/crispy-forms/uni-form.css',
            'libs/crispy-forms/default.uni-form.css',
            'libs/chosen/chosen.css',
            'libs/tipsy/tipsy.css',
            'libs/jTour/jquery-jtour-2.0.2.css',

            'css/hlist.css',
            'css/tabs.css',
            'css/gray-theme.css',
            'css/typography.css',
            'css/deco.css',
            'css/style.css',
        ),
    })

    if settings.DEBUG:
        js = (
            'libs/jquery.js',
            'libs/jquery-ui/jquery-ui.js',
            'libs/openapi.js',
        )
    else:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js',
            'http://userapi.com/js/api/openapi.js?49', # VKontakte
        )

    js += (
        'libs/underscore.js',
        'libs/json2.js',
        'libs/backbone.js',
        'libs/chosen/chosen.jquery.min.js',
        'libs/jquery.placeholder.min.js',
        'libs/jquery.autosize.js',
        reverse('code_data') if settings.DEBUG else 'js/code_data.js',
        'js/main.js',
        'js/resources.js',
        'js/comments.js',
        'js/locations.js',
    )
    media.add_js(js)

    bottom_media = Media()
    bottom_media.add_js((
        'libs/tipsy/jquery.tipsy.js',
        'libs/mustache.js',
        'libs/crispy-forms/uni-form.jquery.js', # TODO: currently doesn't work
        'libs/jTour/jquery-jtour-2.0.2.min.js',
        'js/tour.js',
    ))

    return {'media_files': media, 'bottom_media_files': bottom_media}

def code_data(request):
    ctx = project_settings()

    ctx.update({
        'full_page_url': quote((settings.URL_PREFIX+request.get_full_path()).encode('utf8')),
        'PROFILE': json.dumps(request.PROFILE, ensure_ascii=False),
    })
    return ctx
