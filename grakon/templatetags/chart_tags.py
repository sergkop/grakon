from django import template

register = template.Library()

@register.simple_tag()
def bar_chart(values, labels, size='580x150'):
    """ values is a list of values or [values_list1, values_list2] """
    if len(values)==2 and type(values[0]) is list:
        chd = ','.join(str(val) for val in values[0]) + '|' + ','.join(str(val) for val in values[1])
    else:
        chd = ','.join(str(val) for val in values)

    return '<img width="570" height="150" src="http://chart.apis.google.com/chart?cht=bvs&chco=4D89F9,C6D9FD&chbh=a&chxt=x,y&chds=a&chs=%(size)s&chd=t:%(chd)s&chxl=0:|%(captions)s"/>' % {
        'size': size,
        'chd': chd,
        'captions': '|'.join(str(label) for label in labels),
    }
