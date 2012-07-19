# -*- coding:utf-8 -*-
from django.forms.widgets import DateTimeInput
from django.utils.safestring import mark_safe

# TODO: compress and merge media files
class DateTimeWidget(DateTimeInput):
    class Media:
        css = {
            'all': ('libs/timepicker/timepicker.css',)
        }
        js = ('libs/timepicker/timepicker.js',)

    # TODO: raises errors when used in admin
    def render(self, name, value, attrs=None):
        html = super(DateTimeWidget, self).render(name, value, attrs)
        html += '<script type="text/javascript">' \
                    '$(function(){' \
                        'var datetime_input = $("#id_%(name)s");' \
                        'datetime_input.datetimepicker({' \
                            'stepMinute: 10,' \
                            u'timeText: "Время",' \
                            u'hourText: "Часы",' \
                            u'minuteText: "Минуты",' \
                            u'currentText: "Сейчас",' \
                            u'closeText: "Закрыть",' \
                            'dateFormat: "dd/mm/yy",' \
                            'timeFormat: "hh:mm",' \
                            'ampm: false' \
                        '});' \
                    '});' \
                '</script>' % {'name': name}
        return mark_safe(html)
