from django.conf.urls.defaults import patterns, url

from posts.views import PostParticipantsView, PostView, PostWallView

urlpatterns = patterns('posts.views',
    url(r'^p/(?P<id>\d+)$', PostView.as_view(), name='post'),
    url(r'^p/(?P<id>\d+)/wall', PostWallView.as_view(), name='post_wall'),
    url(r'^p/(?P<id>\d+)/participants', PostParticipantsView.as_view(), name='post_participants'),
    url(r'^p/(?P<id>\d+)/edit$', 'edit_post', name='edit_post'),

    url(r'^add_post$', 'add_post', name='add_post'),
)
