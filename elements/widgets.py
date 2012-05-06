# -*- coding:utf-8 -*-
import json

from django.forms.widgets import SelectMultiple, Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class LocationSelectWidget(Widget):
    def render(self, name, value, attrs=None):
        """ value is a location path - the list [region_id, district_id, location_id] """
        value = value or []

        html = '<div id="%s">%s</div>' % (name, render_to_string('elements/select_location.html'))
        html += '<script type="text/javascript">' \
                    '$().ready(function(){' \
                        '(new SelectLocation({el: $("#%s"), path: %s})).render();' \
                    '});' \
                '</script>' % (name, json.dumps(value))

        # TODO: what is 'test' value for?
        html += '<input type="text" name="%s" style="display:none;" value="test" />' % name

        return mark_safe(html)

# TODO: set default text when nothing is selected
class ResourcesSelectWidget(SelectMultiple):
    def render(self, name, value, attrs=None):
        html = super(ResourcesSelectWidget, self).render(name, value, attrs)
        html += '<script type="text/javascript">' \
                    'var select = $("#id_%(name)s");' \
                    u'select.attr("data-placeholder", "Выберите навыки и ресурсы");' \
                    'if (!select.hasClass("chzn-done"))' \
                        'select.chosen();' \
                    'select.trigger("liszt:updated");' \
                '</script>' % {'name': name}
        return mark_safe(html)
