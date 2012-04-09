from django.conf.urls.defaults import *

from locations.views import LocationView

urlpatterns = patterns('locations.views',
    url(r'^(?P<loc_id>\d+)$', LocationView.as_view(), name='location'),

    url(r'^get_subregions$', 'get_subregions', name='get_subregions'),
)
