# -*- coding:utf-8 -*-
from urllib import quote

from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.widgets import Media

from grakon.utils import project_settings
from posts.models import OPINION_CHOICES

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

            'css/hlist.css',
            'css/tabs.css',
            'css/gray-theme.css',
            'css/typography.css',
            'css/deco.css',
            'css/style.css',
        ),
    })

    if settings.DEBUG:
        js = ('libs/jquery.js', 'libs/jquery-ui/jquery-ui.js', 'libs/openapi.js')
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
        'libs/crispy-forms/uni-form.jquery.js',
        'libs/chosen/chosen.jquery.min.js',
        'libs/tipsy/jquery.tipsy.js',
        'libs/jquery.placeholder.min.js',
        reverse('code_data') if settings.DEBUG else 'js/code_data.js', # TODO: needs to be generated
        'js/main.js',
    )
    media.add_js(js)
    return {'media_files': media}

def proj_settings(request):
    ctx = project_settings()
    ctx.update({
        'OPINION_CHOICES': OPINION_CHOICES,
    })
    return ctx

def page_url(request):
    return {'full_page_url': quote(settings.URL_PREFIX+request.get_full_path())}
