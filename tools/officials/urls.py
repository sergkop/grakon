from django.conf.urls.defaults import patterns, url

from tools.officials.views import OfficialParticipantsView, OfficialView, OfficialWallView

urlpatterns = patterns('tools.officials.views',
    url(r'^official/(?P<official_id>\d+)$', OfficialView.as_view(), name='official'),
    url(r'^official/(?P<official_id>\d+)/wall$', OfficialWallView.as_view(), name='official_wall'),
    url(r'^official/(?P<official_id>\d+)/participants$', OfficialParticipantsView.as_view(), name='official_participants'),
    url(r'^official/(?P<official_id>\d+)/edit$', 'edit_official', name='edit_official'),

    url(r'^create_official$', 'create_official', name='create_official'),
)
