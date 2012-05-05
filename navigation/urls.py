# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

def static_tabs_urls(base_template, menu_item, tabs_short):
    """
    tabs_short=[(name, title, temsplate, css_class, view), ...]
    name here coincides with url slug.
    """
    tabs = [(name, title, '/'+name, template, css_class)
            for name, title, template, css_class, view in tabs_short]

    urls = []
    for name, title, template, css_class, view in tabs_short:
        urls.append(url(r'^'+name+'$', view or 'navigation.views.static_page',
                {'tab': name, 'template': base_template, 'tabs': tabs, 'menu_item': menu_item}, name=name))

    return urls

urlpatterns = patterns('',
    url(r'^$', 'navigation.views.main', name='main'),
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/about/base.html', 'about', [
        ('about', u'Описание', 'static_pages/about/about.html', '', ''),
        ('publications', u'О нас в СМИ', 'static_pages/about/publications.html', '', ''),
    ])
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/feedback/base.html', 'help', [
        ('feedback', u'Обратная связь', 'feedback/feedback.html', '',
                'navigation.views.feedback'),
    ])
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/ideas-test/base.html', '', [
        ('ideas-test', u'Описание', 'static_pages/ideas-test/test.html', '', ''),
    ])
)

urlpatterns += patterns('',
    url('^feedback_thanks$', 'navigation.views.feedback_thanks', name='feedback_thanks'),
)
