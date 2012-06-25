from django.conf.urls import patterns, url

urlpatterns = patterns('search.views',
    url(r'^search/', 'search'),
)
