# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

def static_url(name, template, tabs=[]):
    return url(r'^'+name+'$', 'static_page',
            {'tab': name, 'template': template, 'tabs': tabs}, name=name)

def static_tabs_urls(base_template, tabs_short):
    """
    tabs_short=[(name, title, temsplate, css_class), ...]
    name here coincides with url slug.
    """
    tabs = [{'name': name, 'title': title, 'url': '/'+name,
            'template': template, 'css_class': css_class}
            for name, title, template, css_class in tabs_short]

    return [static_url(name, base_template, tabs)
            for name, title, template, css_class in tabs_short]

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),

    *static_tabs_urls('static_pages/about/base.html', [
        ('about', u'Описание', 'static_pages/about/about.html', ''),
        ('publications', u'О нас в СМИ', 'static_pages/about/publications.html', ''),
    ])
)
