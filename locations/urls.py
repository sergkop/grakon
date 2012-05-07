from django.conf.urls.defaults import patterns, url

from locations.views import MapLocationView, ParticipantsLocationView, ToolsLocationView, WallLocationView

urlpatterns = patterns('locations.views',
    #url(r'^(?P<loc_id>\d+)/map$', MapLocationView.as_view(), name='location_map'),
    url(r'^(?P<loc_id>\d+)/participants$', ParticipantsLocationView.as_view(), name='location_participants'),
    url(r'^(?P<loc_id>\d+)/tools$', ToolsLocationView.as_view(), name='location_tools'),
    url(r'^(?P<loc_id>\d+)/wall$', WallLocationView.as_view(), name='location_wall'),

    url(r'^get_subregions$', 'get_subregions', name='get_subregions'),
    url(r'^goto_location$', 'goto_location', name='goto_location'),
)
