import base64
import json
import hashlib
import hmac
from math import ceil
import time

from django.conf import settings

import bleach
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

def form_helper(action_name, button_name):
    """ Shortcut to generate django-crispy-forms helper """
    helper = FormHelper()
    helper.form_action = action_name
    helper.form_method = 'POST'
    helper.add_input(Submit('', button_name, css_class='gr-blue-button ui-state-default'))
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

def disqus_sso_message(profile):
    """ Take user profile or None """
    if profile:
        data = json.dumps({
            'id': profile.username+str(profile.id),
            'username': unicode(profile),
            'email': profile.user.email,
            'url': settings.URL_PREFIX+profile.get_absolute_url(),
            # TODO: avatar
        })
    else:
        data = '{}'

    message = base64.b64encode(data)
    timestamp = int(time.time())
    sig = hmac.HMAC(settings.DISQUS_SECRET_KEY, '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()
    return message + ' ' + sig + ' ' + str(timestamp)

def disqus_page_params(identifier, url, category):
    return {
        'disqus_identifier': identifier,
        'disqus_url': settings.DISQUS_URL_PREFIX+url,
        'disqus_category_id': settings.DISQUS_CATEGORIES[category],
        'disqus_partial_url': url,
    }

def paginator_params(page, per_page):
    """ page and per_page can be str """
    try:
        page = max(int(page), 1)
    except ValueError:
        page = 1

    try:
        per_page = max(min(int(per_page), 100), 1)
    except ValueError:
        per_page = 20

    return page, per_page

# TODO: what if count==0?
def paginator_data(page, per_page, count, url_prefix):
    num_pages = int(ceil(count/float(per_page)))
    return {
        'page': page,
        'has_prev': page>1,
        'prev_page': page-1,
        'has_next': page<num_pages,
        'next_page': page+1,
        'pages': range(1, num_pages+1),
        'url_prefix': url_prefix,
    }
