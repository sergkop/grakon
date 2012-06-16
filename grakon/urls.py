from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^location/', include('locations.urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^', include('authentication.urls')),
    url(r'^', include('elements.urls')),
    url(r'^', include('navigation.urls')),
    url(r'^', include('users.urls')),
    #url(r'^', include('tools.events.urls')),
    #url(r'^', include('tools.officials.urls')),
    url(r'^', include('tools.tasks.urls')),
    url(r'^', include('tools.ideas.urls')),
    url(r'^', include('tools.projects.urls')),
    url(r'^', include('posts.urls')),

    url(r'', include('social_auth.urls')),
    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^img1x1$', 'grakon.views.img1x1', name='img1x1'), # used to trace emails opening

    url(r'^%s/' % settings.ADMIN_PREFIX, include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^code_data$', 'grakon.views.code_data', name='code_data'),
        (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    )
