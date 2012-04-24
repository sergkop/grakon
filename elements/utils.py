from django.core.cache import cache

import bleach
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

def form_helper(action_name, button_name):
    """ Shortcut to generate django-crispy-forms helper """
    helper = FormHelper()
    helper.form_action = action_name
    helper.form_method = 'POST'
    helper.add_input(Submit('', button_name, css_class='ui-button ui-state-default'))
    return helper

def reset_cache(func):
    """ Decorator for model methods to reset cache key """
    def new_func(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        self.clear_cache()
        return res
    return new_func

# TODO: sync it with tinymce and test
def clean_html(html):
    """ Clean html fields edited by tinymce """
    tags = ['a', 'address', 'b', 'big', 'br', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 
                'ol', 'p', 'pre', 's', 'span', 'strike', 'strong', 'sub', 'sup', 'u', 'ul']

    attributes = ['align', 'alt', 'border', 'class', 'dir', 'data', 'height', 'href', 'id', 'lang', 'longdesc', 'media', 'multiple',
                'nowrap', 'rel', 'rev', 'span', 'src', 'style', 'target', 'title', 'type', 'valign', 'vspace', 'width']

    styles = ['text-decoration', 'font-size', 'font-family', 'text-align', 'padding-left', 'color', 'background-color', ]
    return bleach.clean(html, tags=tags, attributes=attributes, styles=styles, strip=True)
