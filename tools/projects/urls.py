from django.conf.urls.defaults import patterns, url

from tools.projects.views import ProjectParticipantsView, ProjectView, ProjectWallView

urlpatterns = patterns('tools.projects.views',
    url(r'^project/(?P<id>\d+)$', ProjectView.as_view(), name='project'),
    url(r'^project/(?P<id>\d+)/wall$', ProjectWallView.as_view(), name='project_wall'),
    url(r'^project/(?P<id>\d+)/participants$', ProjectParticipantsView.as_view(), name='project_participants'),

    url(r'^create_project$', 'create_project', name='create_project'),
)
