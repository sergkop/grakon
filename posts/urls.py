from django.conf.urls.defaults import patterns, url

from posts.views import PostView

urlpatterns = patterns('posts.views',
    url(r'^(?P<post_id>\d+)$', PostView.as_view(), name='post'),
    url(r'^add_post$', 'add_post', name='add_post'),
)
