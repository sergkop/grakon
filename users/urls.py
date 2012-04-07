from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('users.views',
    url(r'^user/(?P<username>[\w\.]+)/edit$', 'edit_profile', name='edit_profile'),
    url(r'^user/(?P<username>[\w\.]+)$', 'view_profile', name='profile'),

    url(r'^remove_account$', 'remove_account', name='remove_account'),
)
