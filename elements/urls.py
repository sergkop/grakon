from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^add_follower$', 'elements.followers.views.add_follower', name='add_follower'),
    url(r'^remove_follower$', 'elements.followers.views.remove_follower', name='remove_follower'),

    url(r'^add_location$', 'elements.locations.views.add_location', name='add_location'),
    url(r'^remove_location$', 'elements.locations.views.remove_location', name='remove_location'),

    #url(r'^update_resources$', 'update_resources', name='update_resources'),
)
