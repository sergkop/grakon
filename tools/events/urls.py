from django.conf.urls.defaults import patterns, url

from tools.events.views import EventParticipantsView, EventView

urlpatterns = patterns('tools.events.views',
    url(r'^event/(?P<id>\d+)$', EventView.as_view(), name='event'),
    url(r'^event/(?P<id>\d+)/participants', EventParticipantsView.as_view(), name='event_participants'),
    url(r'^event/(?P<id>\d+)/edit$', 'edit_event', name='edit_event'),

    url(r'^create_event$', 'create_event', name='create_event'),
)
