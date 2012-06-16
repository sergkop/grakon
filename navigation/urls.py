# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'navigation.views.main', name='main'),
    url('^feedback_thanks$', 'navigation.views.feedback_thanks', name='feedback_thanks'),
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
        }
        urls.append(url(r'^'+name+'$', view or 'navigation.views.static_page',
                kwargs, name=name))

    return urls

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/about/base.html', [
        ('about', u'Описание', 'static_pages/about/about.html', '', ''),
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

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/partners/base.html', [
        ('partners', u'Наши партнеры', 'static_pages/partners/partners.html', '', ''),
    ])
)

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/feedback/base.html', [
        ('feedback', u'Обратная связь', 'feedback/feedback.html', '',
                'navigation.views.feedback'),
    ])
)
