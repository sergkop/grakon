from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('elements.views',
    url(r'^add_follower$', 'add_follower', name='add_follower'),
    url(r'^remove_follower$', 'remove_follower', name='remove_follower'),
    url(r'^update_resources$', 'update_resources', name='update_resources'),
    url(r'^add_location$', 'add_location', name='add_location'),
    url(r'^remove_location$', 'remove_location', name='remove_location'),
)


