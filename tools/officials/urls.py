from django.conf.urls.defaults import patterns, url

from tools.officials.views import OfficialAdminsView, OfficialFollowersView, OfficialView

urlpatterns = patterns('tools.officials.views',
    url(r'^official/(?P<official_id>\d+)$', OfficialView.as_view(), name='official'),
    url(r'^official/(?P<official_id>\d+)/followers$', OfficialFollowersView.as_view(), name='official_followers'),
    url(r'^official/(?P<official_id>\d+)/admins$', OfficialAdminsView.as_view(), name='official_admins'),
    url(r'^official/(?P<official_id>\d+)/edit$', 'edit_official', name='edit_official'),

    url(r'^create_official$', 'create_official', name='create_official'),
)
