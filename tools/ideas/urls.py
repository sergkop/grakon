from django.conf.urls.defaults import patterns, url

from tools.ideas.views import IdeaView

urlpatterns = patterns('',
    url(r'^idea/(?P<id>\d+)$', IdeaView.as_view(), name='idea'),
)
