# -*- coding:utf-8 -*-
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from elements.models import HTMLField
from elements.participants.models import EntityParticipant, ROLE_TYPES
from elements.utils import check_permissions, clean_html, entity_post_method, table_data

# TODO: if there is a single location - add to ctx (admin as well?)
def entity_base_view(view, entity_model, selector):
    """ selector is a dict uniquely identifying the entity """
    view.entity = get_object_or_404(entity_model, **selector)
    view.info = view.entity.info()

    ctx = {'info': view.info}

    # TODO: all data can be recieved in one db query
    for role in entity_model.roles:
        if view.request.user.is_authenticated():
            ctx['is_'+role] = EntityParticipant.objects.is_participant(view.entity, view.request.profile, role)
        else:
            ctx['is_'+role] = False

    ctx.update(view.update_context())
    return ctx

def entity_tabs_view(view):
    return {
        'tab': view.tab,
        'tabs': view.tabs,
        'template_path': filter(lambda t: t[0]==view.tab, view.tabs)[0][3],
    }

# TODO: fix it
def participants_view(view):
    roles = type(view.entity).roles

    # TODO: take plural and template from entity model (?)
    titles = dict((rl, plural) for rl, single, plural in ROLE_TYPES if rl in roles)

    role = view.request.GET.get('type', '')
    if role not in roles:
        role = roles[0]

    ctx = table_data(view.request, 'participants', getattr(view.entity, 'get_'+role))
    ctx.update({
        'table_cap_choices': [(view.participants_url+'?type='+rl, titles[rl]) for rl in roles],
        'table_cap_title': titles[role],
        'table_cap_template': 'participants/%s_button.html' % role,
    })
    return ctx

@entity_post_method
@check_permissions
def update_text_field(request, entity):
    field = request.POST.get('field', '')
    if field not in type(entity).editable_fields:
        return HttpResponse(u'Это поле нельзя редактировать')

    value = request.POST.get('value', '')

    model_field = type(entity)._meta.get_field(field)
    if type(model_field) is models.CharField:
        value = value[:model_field.max_length]
    elif type(model_field) is HTMLField:
        value = clean_html(value)
    else:
        assert False, "Field %s of entity model %s should not be editable" % (field, model_field.__name__)

    setattr(entity, field, value)
    entity.save()

    return HttpResponse('ok')
