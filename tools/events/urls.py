from django.conf.urls.defaults import patterns, url

from tools.events.views import EventAdminsView, EventFollowersView, EventView

urlpatterns = patterns('tools.events.views',
    url(r'^event/(?P<event_id>\d+)$', EventView.as_view(), name='event'),
    url(r'^event/(?P<event_id>\d+)/followers$', EventFollowersView.as_view(), name='event_followers'),
    url(r'^event/(?P<event_id>\d+)/admins$', EventAdminsView.as_view(), name='event_admins'),
    url(r'^event/(?P<event_id>\d+)/edit$', 'edit_event', name='edit_event'),

    url(r'^create_event$', 'create_event', name='create_event'),
)
