from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tools.officials.views',
    url(r'^official/(?P<official_id>\d+)$', 'view_official', name='official'),
    url(r'^official/(?P<official_id>\d+)/followers$', 'official_followers', name='official_followers'),
    url(r'^official/(?P<official_id>\d+)/admins$', 'official_admins', name='official_admins'),
    url(r'^official/(?P<official_id>\d+)/edit$', 'edit_official', name='edit_official'),

    url(r'^create_official$', 'create_official', name='create_official'),
)
