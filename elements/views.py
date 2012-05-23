from django.shortcuts import get_object_or_404

from elements.participants.models import EntityParticipant, ROLE_TYPES
from elements.utils import table_data

def entity_base_view(view, entity_model, id):
    view.entity = get_object_or_404(entity_model, id=id)

    ctx = {
        'tools_menu_item': True,
        'tab': view.tab,
        'participants_url': view.participants_url,
        'info': view.entity.info(),
    }

    # TODO: all data can be recieved in one db query
    for role in entity_model.roles:
        if view.request.user.is_authenticated():
            ctx['is_'+role] = EntityParticipant.objects.is_participant(view.entity, view.request.profile, role)
        else:
            ctx['is_'+role] = False

    ctx.update(view.update_context())
    return ctx

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

#from django.http import HttpResponse
#from elements.utils import check_permissions, entity_post_method
# TODO: depricate or move to resources
#@entity_post_method
#@check_permissions
#def update_resources(request, entity):
#    EntityResource.objects.update(entity, request.POST.getlist('value[]', None))
#    return HttpResponse('ok')
