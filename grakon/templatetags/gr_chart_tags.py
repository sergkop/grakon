from django import template

register = template.Library()

API_URL = 'http://chart.apis.google.com/chart'

@register.inclusion_tag('dashboard/bar_chart.html')
def gr_bar_chart(values, captions, size='580x150', caption=''):
    return {
        'values': values,
        'captions': captions,
        'size': size,
        'max_value': max(values) if len(values) > 0 else 0,
        'caption': caption.replace(' ', '+'),
    }
