from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

register = template.Library()

@register.inclusion_tag('elements/button.html')
def button(icon, title, id=None, link='', center='center', tip=''):
    """ link is either a url, starting with http:// or https://, or the name of a view """
    if link!='' and not link.startswith('http://') and not link.startswith('https://') and not link.startswith('mailto:'):
        link = reverse(link)

    external = link.startswith('http') if link else False

    return {'icon': icon, 'title': title, 'id': id, 'link': link,
            'external': external, 'center': center!='', 'tip': tip}

@register.tag(name="tabs")
def tabs_tag(parser, token):
    args = token.split_contents()
    if len(args) != 4:
        raise template.TemplateSyntaxError("tabs tag takes exactly 3 arguments")
    return TabsNode(*args[1:])

class TabsNode(template.Node):
    def __init__(self, *args):
        """
        args is a sequence of id, tabs, active_tab.
        tabs is a list of tuples (name, title, url, template, css_class).
        """
        self.args = [template.Variable(arg) for arg in args]

    def render(self, context):
        id, tabs, active = self.args = [arg.resolve(context) for arg in self.args]

        active_tabs = filter(lambda tab: tab[0]==active, tabs)
        assert len(active_tabs)==1, "Active tab must be uniquely identified"

        context.update({
            'id': id,
            'tabs': tabs,
            'template_path': active_tabs[0][3],
            'active': active
        })
        return render_to_string('elements/tabs.html', context)
