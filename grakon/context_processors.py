# -*- coding:utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.widgets import Media

# TODO: add IE-specific styles here
# TODO: take extra media files from request - ability to add them per-view (variable in class-based views?)
def media_files(request):
    media = Media()
    media.add_css({
        'all': (
            'libs/yaml/base.min.css',
            'libs/jquery-ui/jquery-ui.css',
            'libs/crispy-forms/uni-form.css',
            'libs/crispy-forms/default.uni-form.css',
            'libs/chosen/chosen.css',
            #'libs/tipsy/tipsy.css',

            'css/layout.css',
            'css/typography.css',
            'css/hlist.css',
            'css/style.css',
            'css/julia_style.css',
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
        #'libs/tipsy/jquery.tipsy.js',
        reverse('code_data') if settings.DEBUG else 'js/code_data.js', # TODO: needs to be generated
        'js/main.js',
    )
    media.add_js(js)
    return {'media_files': media}

def project_settings(request):
    context = {}
    for setting in ('VK_APP_ID', 'GOOGLE_ANALYTICS_ID', 'YA_METRIKA_ID', 'YANDEX_MAPS_KEY',
            'URL_PREFIX', 'ADMIN_EMAIL', 'ADMIN_PREFIX', 'DEBUG'):
        context[setting] = getattr(settings, setting)

    context['SLOGAN'] = u'Гражданский контроль за работой властей'
    return context
