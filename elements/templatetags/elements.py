from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.tag(name="tabs")
def tabs_tag(parser, token):
    args = token.split_contents()
    if len(args) != 3:
        raise template.TemplateSyntaxError("tabs tag takes exactly 2 arguments")
    return TabsNode(*args[1:])

class TabsNode(template.Node):
    def __init__(self, *args):
        """
        args is a sequence of tabs, active_tab.
        tabs is a list of tuples (name, title, url, template, css_class).
        """
        self.args = [template.Variable(arg) for arg in args]

    def render(self, context):
        tabs, active = self.args = [arg.resolve(context) for arg in self.args]

        active_tabs = filter(lambda tab: tab[0]==active, tabs)
        assert len(active_tabs)==1, "Active tab must be uniquely identified"

        context.update({
            'tabs': tabs,
            'template_path': active_tabs[0][3],
            'active': active
        })
        return render_to_string('elements/tabs.html', context)
