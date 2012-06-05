# -*- coding:utf-8 -*-
from django.http import HttpResponse

from elements.resources.models import EntityResource
from elements.utils import is_entity_admin, entity_post_method

@entity_post_method
def add_resource(request, entity):
    if request.POST.get('provider')=='true':
        provider = request.profile
    else:
        if not is_entity_admin(entity, request.profile):
            return HttpResponse(u'У вас нет прав на выполнение этой операции')
        provider = None

    EntityResource.objects.add_or_update(entity, request.POST.get('resource', ''),
            request.POST.get('description', ''), provider)

    #EntityResource.objects.update(entity, request.POST.getlist('value[]', None))
    return HttpResponse('ok')

# TODO: add_resource and remove_resource have repeating code
@entity_post_method
def remove_resource(request, entity):
    if request.POST.get('provider')=='true':
        provider = request.profile
    else:
        if not is_entity_admin(entity, request.profile):
            return HttpResponse(u'У вас нет прав на выполнение этой операции')
        provider = None

    EntityResource.objects.remove(entity, request.POST.get('resource', ''), provider)
    return HttpResponse('ok')
