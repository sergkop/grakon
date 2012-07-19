from django.conf.urls.defaults import patterns, url

from users.views import ProfileIdeasView, ProfileProjectsView, ProfileTasksView, ProfileView

urlpatterns = patterns('users.views',
    url(r'^user/(?P<id>\d+)$', ProfileView.as_view(), name='profile'),
    url(r'^user/(?P<id>\d+)/tasks$', ProfileTasksView.as_view(), name='profile_tasks'),
    url(r'^user/(?P<id>\d+)/projects$', ProfileProjectsView.as_view(), name='profile_projects'),
    url(r'^user/(?P<id>\d+)/ideas$', ProfileIdeasView.as_view(), name='profile_ideas'),

    url(r'^profile$', 'profile', name='profile'),

    url(r'^remove_account$', 'remove_account', name='remove_account'),

    url(r'^send_message$', 'send_message', name='send_message'),
)
