# -*- coding:utf-8 -*-
from math import ceil

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
    helper.add_input(Submit('', button_name, css_class='ym-button'))
    return helper

def reset_cache(func):
    """ Decorator for model methods to reset cache key """
    def new_func(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        self.clear_cache()
        return res
    return new_func

# TODO: sync it with tinymce and test
# TODO: remove all <p></p>. Replace them with <br/> (?)
def clean_html(html):
    """ Clean html fields edited by tinymce """
    tags = ['a', 'b', 'br', 'em', 'i', 'li', 'ol', 'p', 'span', 'strong', 'u', 'ul']

    attributes = ['align', 'href', 'style', 'target', 'rel']

    styles = ['text-decoration']
    html = bleach.clean(html, tags=tags, attributes=attributes, styles=styles, strip=True)
    return bleach.linkify(html, nofollow=True, target='_blank')

# TODO: use anchors to show table on navigation to another page
def table_data(request, entity_type, selector, limit=20):
    """ selector(start, limit, sort_by) """
    try:
        page = max(int(request.GET.get('page', 0)), 1)
    except ValueError:
        page = 1

    try:
        per_page = max(min(int(limit), 100), 1)
    except ValueError:
        per_page = 20

    from elements.models import ENTITIES_MODELS
    entity_model = ENTITIES_MODELS[entity_type]
    entities_data = selector(start=(page-1)*per_page, limit=per_page)
    entities_info = entity_model.objects.info_for(entities_data['ids'], related=True)
    entities = [entities_info[id] for id in entities_data['ids'] if id in entities_info]

    # TODO: allow to choose limit (?)
    url_prefix = '?' # TODO: add sorting and limit (per_page) params - don't do it unless they differ from default

    num_pages = int(ceil(entities_data['count']/float(per_page)))

    # TODO: what if count==0?
    return {
        'pagination_entities': entities,
        'paginator': {
            'page': page,
            'has_prev': page>1,
            'prev_page': page-1,
            'has_next': page<num_pages,
            'next_page': page+1,
            'pages': range(1, num_pages+1),
            'url_prefix': url_prefix,
        },
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

def is_entity_admin(entity, profile):
    from users.models import Profile
    if type(entity) is Profile:
        return entity == profile
    elif 'participants' in type(entity).features and 'admin' in type(entity).roles:
        from elements.participants.models import EntityParticipant
        return EntityParticipant.objects.is_participant(entity, profile, 'admin')
    else:
        return False

def provided_entity_method(func):
    """
    Декоратор для entity_post_method view. Пытается достать провайдера и проверить из запроса.
    Посылает провайдер 3м аргументом в декорированный метод
    """
    def wrapper(request, entity):

        if request.POST.get('provider')=='true':
            provider = request.profile
        else:
            if not is_entity_admin(entity, request.profile):
                return HttpResponse(u'У вас нет прав на выполнение этой операции')
            provider = None

        return func(request, entity, provider)
    return wrapper

def check_permissions(func):
    """ Check if user has permissions to modify entity """
    def new_func(request, entity):
        if not is_entity_admin(entity, request.profile):
            return HttpResponse(u'У вас нет прав на выполнение этой операции')
        return func(request, entity)
    return new_func
