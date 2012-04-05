from django.conf.urls.defaults import patterns, url

def static_url(name, template, tabs=[]):
    return url(r'^'+name+'$', 'static_page',
            {'tab': name, 'template': template, 'tabs': tabs}, name=name)

def static_tabs_urls(base_template, tabs_short):
    """ tabs_short=[(name, template, css_class), ...] """
    tabs = [(name, '/'+name, template, css_class)
            for name, template, css_class in tabs_short]

    return patterns('navigation.views',
            *[static_url(name, base_template, tabs) \
            for name, template, css_class in tabs_short])

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),
)

urlpatterns += static_tabs_urls('static_pages/about/base.html', [
    ('about', 'static_pages/about/about.html', ''),
])
