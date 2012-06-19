from django.utils.translation import ugettext as __
from django import template

register = template.Library()
API_URL = 'http://chart.apis.google.com/chart'

@register.inclusion_tag('dashboard/bar_chart.html')
def gr_bar_chart(values, captions, size='580x150',caption="", max_value=None):
    if len(values)>0:
        max_value = max_value or max(values)
    else:
        max_value = 0
    cap = __(caption)
    return {
        'values': values,
        'captions': captions,
        'size': size,
        'max_value': max_value,
        'caption':cap.replace(" ","+"),
    }

