from django.conf.urls.defaults import patterns, url

def static_url(name, template):
    return url(r'^'+name+'$', 'static_page', {'name': name, 'template': template}, name=name)

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),

    static_url('about', 'static_pages/about/base.html'),
)
