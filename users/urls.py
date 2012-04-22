from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('users.views',
    url(r'^user/(?P<username>[\w\.]+)/edit$', 'edit_profile', name='edit_profile'),
    url(r'^user/(?P<username>[\w\.]+)$', 'view_profile', name='profile'),

    url(r'^profile$', 'profile', name='profile'),

    url(r'^update_resources$', 'update_resources', name='update_resources'),

    url(r'^remove_account$', 'remove_account', name='remove_account'),
)
