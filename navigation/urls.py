# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),
    url(r'^feedback$', 'feedback', name='feedback'),
    url('^feedback_thanks$', 'static_page', kwargs={'template': 'feedback/thanks.html'}, name='feedback_thanks'),
    url('^partners$', 'static_page', kwargs={'template': 'static_pages/partners.html', 'title': u'Партнеры'}, name='partners'),
)

def static_tabs_urls(base_template, tabs_short):
    """
    tabs_short=[(name, title, temsplate, css_class, view), ...]
    name here coincides with url slug.
    """
    tabs = [(name, title, '/'+name, template, css_class)
            for name, title, template, css_class, view in tabs_short]

    urls = []
    for name, title, template, css_class, view in tabs_short:
        kwargs = {
            'tab': name,
            'template': base_template,
            'tabs': tabs,
            'template_path': template,
            'title': title,
        }
        urls.append(url(r'^'+name+'$', view or 'navigation.views.static_page',
                kwargs, name=name))

    return urls

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/about/base.html', [
        ('about', u'Описание', 'static_pages/about/about.html', '', ''),
        ('rules', u'Правила площадки', 'static_pages/about/rules.html', '', ''),
        ('publications', u'О нас в СМИ', 'static_pages/about/publications.html', '', ''),
    ])
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/how_to_help/base.html', [
        ('how_to_help', u'...мозгами', 'static_pages/how_to_help/join_us.html', '', ''),
        ('donate', u'...деньгами', 'static_pages/how_to_help/donate.html', '', ''),
        ('volunteer', u'... как волонтер', 'static_pages/how_to_help/volunteer.html', '', ''),
        ('share', u'... распространить информацию', 'static_pages/how_to_help/share.html', '', ''),
    ])
)
