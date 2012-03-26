from django.conf import settings
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
            #'libs/tipsy/tipsy.css',

            'css/layout.css',
            'css/typography.css',
            'css/hlist.css',
            'css/style.css',
            'css/julia_style.css',
        ),
    })

    if settings.DEBUG:
        js = ('libs/jquery.js', 'libs/jquery-ui/jquery-ui.js')
    else:
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
                'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js')

    js += (
        'http://userapi.com/js/api/openapi.js?49', # VKontakte
        'libs/crispy-forms/uni-form.jquery.js',
        #'libs/tipsy/jquery.tipsy.js',
    )
    media.add_js(js)
    return {'media_files': media}

def project_settings(request):
    context = {}
    for setting in ('VK_APP_ID', 'GOOGLE_ANALYTICS_ID', 'YA_METRIKA_ID', 'YANDEX_MAPS_KEY', 'URL_PREFIX'):
        context[setting] = getattr(settings, setting)
    return context
