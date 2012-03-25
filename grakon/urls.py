from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('auth.urls')),
    url(r'^', include('navigation.urls')),

    url(r'^tinymce/', include('tinymce.urls')),

    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),

    url(r'^%s/' % settings.ADMIN_PREFIX, include(admin.site.urls)),
)
