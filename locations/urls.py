from django.conf.urls.defaults import patterns, url

from locations.views import LocationProjectsView, LocationTasksView, LocationWallView, ParticipantsLocationView

urlpatterns = patterns('locations.views',
    #url(r'^(?P<loc_id>\d+)/map$', MapLocationView.as_view(), name='location_map'),
    #url(r'^(?P<loc_id>\d+)/tools$', ToolsLocationView.as_view(), name='location_tools'),
    url(r'^(?P<loc_id>\d+)/participants$', ParticipantsLocationView.as_view(), name='location_participants'),
    url(r'^(?P<loc_id>\d+)/wall$', LocationWallView.as_view(), name='location_wall'),
    url(r'^(?P<loc_id>\d+)/tasks$', LocationTasksView.as_view(), name='location_tasks'),
    url(r'^(?P<loc_id>\d+)/projects$', LocationProjectsView.as_view(), name='location_projects'),

    url(r'^get_subregions$', 'get_subregions', name='get_subregions'),
    url(r'^goto_location$', 'goto_location', name='goto_location'),
)
