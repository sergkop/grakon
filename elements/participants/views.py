# -*- coding:utf-8 -*-
from django.http import HttpResponse

from elements.participants.models import EntityParticipant
from elements.utils import entity_post_method

# TODO: admin role requires special processing (permissions)
@entity_post_method
def add_participant(request, entity):
    role = request.POST.get('role', '')
    if role not in ('follower',):
        return HttpResponse(u'Роль указана неверно')

    EntityParticipant.objects.add(entity, request.profile, role)
    # TODO: send letter to user if he is followed (control by settings)
    return HttpResponse('ok')

@entity_post_method
def remove_participant(request, entity):
    role = request.POST.get('role', '')
    if role not in ('follower',):
        return HttpResponse(u'Роль указана неверно')

    EntityParticipant.objects.remove(entity, request.profile, role)
    return HttpResponse('ok')
