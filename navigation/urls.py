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
<<<<<<< HEAD
    *static_tabs_urls('static_pages/about/base.html', 'about', [
=======
    *static_tabs_urls('static_pages/about/base.html', '', [
>>>>>>> 6a9c1f108c2a16ab704068325fee927d64c53299
        ('about', u'Описание', 'static_pages/about/about.html', '', ''),
        ('publications', u'О нас в СМИ', 'static_pages/about/publications.html', '', ''),
    ])
)

urlpatterns += patterns('',
<<<<<<< HEAD
    *static_tabs_urls('static_pages/feedback/base.html', 'help', [
        ('feedback', u'Обратная связь', 'feedback/feedback.html', '',
=======
    *static_tabs_urls('static_pages/ideas-test/base.html', [
        ('test', u'Описание', 'static_pages/ideas-test/test.html', '', ''),
    ])
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/feedback/base.html', [
        ('feedback', u'Обратная связь', 'static_pages/how_to_help/feedback.html', '',
>>>>>>> 6a9c1f108c2a16ab704068325fee927d64c53299
                'navigation.views.feedback'),
    ])
)

urlpatterns += patterns('',
    url('^feedback_thanks$', 'navigation.views.feedback_thanks', name='feedback_thanks'),
)
