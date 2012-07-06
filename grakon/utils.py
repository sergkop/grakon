# -*- coding:utf-8 -*-
import cookielib
from random import choice
import sys
import urllib2

from django.conf import settings
from django.http import HttpResponse

# TODO: add ie and chrome
USER_AGENTS = [
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.5) Gecko/20091114 Gentoo Firefox/3.5.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729)',
    'Opera/9.62 (Windows NT 6.0; U; en) Presto/2.1.1',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3',
]

def read_url(url, encoding='windows-1251'):
    """ Set encoding=None to skip decoding """
    proxy_handler = urllib2.ProxyHandler()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url, headers={'User-Agent': choice(USER_AGENTS)})
    try:
        data = opener.open(request).read()
        if encoding:
            data = data.decode('windows-1251')
        return data
    except urllib2.URLError, e:
        raise e # TODO: what to do here?
        return ''

def escape_html(html):
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def print_progress(i, count):
    """ Show progress message updating in-place """
    if i < count-1:
        sys.stdout.write("\r%(percent)2.3f%%" % {'percent': 100*float(i)/count})
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        sys.stdout.flush()

def authenticated_ajax_post(func):
    def new_func(request):
        if not (request.method=='POST' and request.is_ajax() and request.user.is_authenticated()):
            return HttpResponse(u'Вам необходимо войти в систему')
        return func(request)
    return new_func

def project_settings():
    res = {}
    for setting in ('VK_APP_ID', 'GOOGLE_ANALYTICS_ID', 'YA_METRIKA_ID', 'YANDEX_MAPS_KEY',
            'URL_PREFIX', 'STATIC_URL', 'ADMIN_EMAIL', 'ADMIN_PREFIX', 'DEBUG',
            'LIST_COUNT', 'TINYMCE_COMPRESSOR', 'TINYMCE_JS_URL', 'SLOGAN'):
        res[setting] = getattr(settings, setting)
    return res
