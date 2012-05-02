# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

def static_tabs_urls(base_template, tabs_short):
    """
    tabs_short=[(name, title, temsplate, css_class, view), ...]
    name here coincides with url slug.
    """
    tabs = [(name, title, '/'+name, template, css_class)
            for name, title, template, css_class, view in tabs_short]

    urls = []
    for name, title, template, css_class, view in tabs_short:
        urls.append(url(r'^'+name+'$', view or 'navigation.views.static_page',
                {'tab': name, 'template': base_template, 'tabs': tabs}, name=name))

    return urls

urlpatterns = patterns('',
    url(r'^$', 'navigation.views.main', name='main'),
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/about/base.html', [
        ('about', u'Описание', 'static_pages/about/about.html', '', ''),
        ('publications', u'О нас в СМИ', 'static_pages/about/publications.html', '', ''),
    ])
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/feedback/base.html', [
        ('feedback', u'Обратная связь', 'static_pages/how_to_help/feedback.html', '',
                'navigation.views.feedback'),
    ])
)
