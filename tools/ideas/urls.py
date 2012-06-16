from django.conf.urls.defaults import patterns, url

from tools.ideas.views import add_idea, IdeaView

urlpatterns = patterns('',
    url(r'^idea/(?P<id>\d+)$', IdeaView.as_view(), name='idea'),
    url(r'^add_idea$', add_idea, name='add_idea'),
)
