from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tools.ideas.views',
    url(r'^idea/(?P<id>\d+)$', 'idea_view', name='idea'),
)
