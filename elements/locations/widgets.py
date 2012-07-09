import json

from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class LocationSelectWidget(Widget):
    def render(self, name, value, attrs=None):
        """ value is a location path - the list [region_id, district_id, location_id] """
        value = value or []

        html = '<div id="%s" class="gr-fl">%s</div>' % (name, render_to_string('locations/select.html'))
        html += '<script type="text/javascript">' \
                    '$().ready(function(){' \
                        '(new SelectLocation({el: $("#%s"), path: %s})).render();' \
                    '});' \
                '</script>' % (name, json.dumps(value))

        # value="val" is needed so that form error is not raised because of empty field
        html += '<input type="text" name="%s" style="display:none;" value="val" />' % name

        return mark_safe(html)
