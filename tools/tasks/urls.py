from django.conf.urls.defaults import patterns, url

from tools.tasks.views import TaskView

urlpatterns = patterns('tools.tasks.views',
    url(r'^task/(?P<id>\d+)$', TaskView.as_view(), name='task'),
    url(r'^create_task$', 'create_task', name='create_task'),
)
