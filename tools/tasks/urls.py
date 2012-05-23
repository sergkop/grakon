from django.conf.urls.defaults import patterns, url

from tools.tasks.views import TaskParticipantsView, TaskView, TaskWallView

urlpatterns = patterns('tools.tasks.views',
    url(r'^task/(?P<id>\d+)$', TaskView.as_view(), name='task'),
    url(r'^task/(?P<id>\d+)/wall$', TaskWallView.as_view(), name='task_wall'),
    url(r'^task/(?P<id>\d+)/participants$', TaskParticipantsView.as_view(), name='task_participants'),
    url(r'^task/(?P<id>\d+)/edit$', 'edit_task', name='edit_task'),

    url(r'^create_task$', 'create_task', name='create_task'),
)
