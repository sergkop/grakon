#from django.conf import settings
from django.conf.urls import patterns,url
from django.contrib import admin
#from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('search.views',
    url(r'^search/', 'do_search'),
)

