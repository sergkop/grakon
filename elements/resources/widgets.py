# -*- coding:utf-8 -*-
from django.forms.widgets import Widget, SelectMultiple
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


class ResourceLabelsAreaWidget(Widget):
    """ Виджет представляет из себя div с добавляющимися в него полями ресурсов типа input type=hidden  """
    def render(self, name, value, attrs=None):

        wrapper =  '<div class="gr-ideas-item">' \
                        '%s' \
                   '</div>'

        add_btn =  '<div class="gr-add gr-idea-selected">'\
                        '<span class="gr-add-icon add-resource-btn gr-add-profile" title="%s">&nbsp;</span>'\
                    '</div>' % u"Добавить ресурсы"

        holder =  '<div id="resources_list" class="resources-list gr-mb10">' \
                  '</div>'

        script = '<script type="text/javascript">'\
                    '$(function() {' \
                        'new Resource.ListView({' \
                            'el: $(".resources-list"),' \
                            'addBtn: $(".add-resource-btn"),' \
                            'itemSel: ".gr-resource-item",' \
                            'itemClass: Resource.Form.FItemView,' \
                            'popupClass: Resource.Form.FPopupEditorView' \
                        '});' \
                    '})'\
                 '</script>'

        return mark_safe(wrapper % (add_btn + holder + script))