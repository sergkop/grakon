# -*- coding:utf-8 -*-
import base64
import json
import hashlib
import hmac
from math import ceil
import time

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

import bleach
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from grakon.utils import authenticated_ajax_post

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

# TODO: merge paginator methods in it (?)
def table_data(request, entity_type, selector, limit=20):
    """ selector(start, limit, sort_by) """
    page, per_page = paginator_params(request.GET.get('page', 0), limit)

    from elements.models import ENTITIES_MODELS
    entity_model = ENTITIES_MODELS[entity_type]
    entities_data = selector((page-1)*per_page, limit=per_page)
    entities_info = entity_model.objects.info_for(entities_data['ids'], related=False)
    entities = [entities_info[id] for id in entities_data['ids'] if id in entities_info]

    # TODO: allow to choose limit (?)
    url_prefix = '?' # TODO: add sorting and limit (per_page) params - don't do it unless they differ from default

    # TODO: show count somewhere
    # TODO: generate table header (include sorting links and highlighting arrows)
    return {
        'pagination_entities': entities,
        'paginator': paginator_data(page, per_page, entities_data['count'], url_prefix),
        'header_template': entity_model.table_header,
        'line_template': entity_model.table_line,
    }

def get_entity(post_data):
    """ Shortcut returning entity or None for form data """
    try:
        ct_id = int(post_data.get('ct', ''))
        id = int(post_data.get('id', ''))
    except ValueError:
        return

    try:
        content_type = ContentType.objects.get_for_id(ct_id)
    except ContentType.DoesNotExist:
        return

    model = content_type.model_class()
    try:
        return model.objects.get(id=id)
    except model.DoesNotExist:
        return

def entity_post_method(func):
    """ Shortcut for creating entity ajax ports """
    @authenticated_ajax_post
    def new_func(request):
        entity = get_entity(request.POST)
        if not entity:
            return HttpResponse(u'Запись указана неверно')
        return func(request, entity)
    return new_func

def check_permissions(func):
    """ Check if user has permissions to modify entity """
    from users.models import Profile
    def new_func(request, entity):
        if type(entity) is Profile:
            has_perm = (entity==request.profile)
        else:
            pass # TODO: check that model has admins feature and user is admin

        if not has_perm:
            return HttpResponse(u'У вас нет прав на выполнение этой операции')

        return func(request, entity)

    return new_func
