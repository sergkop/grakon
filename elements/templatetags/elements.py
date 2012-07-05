from django import template
from django.template.loader import render_to_string
from django.utils._os import safe_join

from pystache import Renderer

register = template.Library()

@register.tag(name='tabs')
def tabs_tag(parser, token):
    args = token.split_contents()
    if len(args) != 3:
        raise template.TemplateSyntaxError("tabs tag takes exactly 2 arguments")
    return TabsNode(*args[1:])

class TabsNode(template.Node):
    def __init__(self, *args):
        """
        args is a sequence of tabs, active_tab.
        tabs is a list of tuples (name, title, url, css_class).
        """
        self.args = [template.Variable(arg) for arg in args]

    def render(self, context):
        tabs, active = self.args = [arg.resolve(context) for arg in self.args]

        active_tabs = filter(lambda tab: tab[0]==active, tabs)
        assert len(active_tabs)==1, "Active tab must be uniquely identified"

        context.update({
            'tabs': tabs,
            'active': active
        })
        return render_to_string('elements/tabs.html', context)

def get_mustache_template(path):
    # This code is partially copied from django.template.loaders.app_directories
    from django.template.loaders.app_directories import app_template_dirs
    for template_dir in app_template_dirs:
        try:
            full_path = safe_join(template_dir, path)
        except ValueError:
            pass
        else:
            try:
                file = open(full_path)
                try:
                    return file.read().decode('utf8')
                finally:
                    file.close()
            except IOError:
                pass

def mustache_renderer(partials_paths):
    """ partials_paths = {name: path} """
    partials = {}
    for name, path in partials_paths.iteritems():
        partials[name] = get_mustache_template(path)
    return Renderer(partials=partials)

comments_templates = {
    'comment_item': 'comments/item.mustache',
    'comments_list': 'comments/list.mustache',
    'comment_field': 'comments/field.mustache',
}

@register.simple_tag(takes_context=True)
def show_comments(context, template_path, info):
    template = get_mustache_template(template_path)

    # TODO: check that corresponding entity model has comments feature

    # TODO: move getting renderer out of here
    comments_renderer = mustache_renderer(comments_templates)

    ctx = {
        'ct': info['ct'],
        'e_id': info['instance']['id'],
        'comments': info['comments'],
        'PROFILE': context['request'].PROFILE,
    }
    return comments_renderer.render(template, ctx)


resources_templates = {
    'resources_item': 'resources/item.mustache',
    'resources_list': 'resources/list.mustache',
    'resources_edit_popup': 'resources/edit_popup.mustache',
}

@register.simple_tag(takes_context=True)
def show_resources(context, template_path, resources):
    template = get_mustache_template(template_path)

    comments_renderer = mustache_renderer(resources_templates)
    ctx = {'resources': resources}
    return comments_renderer.render(template, ctx)