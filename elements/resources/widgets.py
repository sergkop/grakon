# -*- coding:utf-8 -*-
from django.forms.widgets import SelectMultiple
from django.utils.safestring import mark_safe

# TODO: set default text when nothing is selected
# TODO: move javascript to main.js
class ResourcesSelectWidget(SelectMultiple):
    def render(self, name, value, attrs=None):
        html = super(ResourcesSelectWidget, self).render(name, value, attrs)
        html += '<script type="text/javascript">' \
                    'select_resources($("#id_%(name)s"));' \
                '</script>' % {'name': name}
        return mark_safe(html)
