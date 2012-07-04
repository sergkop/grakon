# -*- coding:utf-8 -*-
from django.http import HttpResponse

from elements.resources.models import EntityResource
from elements.utils import is_entity_admin, entity_post_method, provided_entity_method

@entity_post_method
@provided_entity_method
def add_resource(request, entity, provider):
    """ Добавляет ресурс """

    EntityResource.objects.add(entity, request.POST.get('resource', ''),
        description=request.POST.get('description', ''), provider=provider)

    #EntityResource.objects.update(entity, request.POST.getlist('value[]', None))
    return HttpResponse('ok')


@entity_post_method
@provided_entity_method
def update_resource(request, entity, provider):
    """ Редактирует существующий ресурс """

    EntityResource.objects.edit(entity, request.POST.get('old_resource', ''), request.POST.get('resource', ''),
        description=request.POST.get('description', ''), provider=provider)

    return HttpResponse('ok')


@entity_post_method
@provided_entity_method
def remove_resource(request, entity, provider):
    """ Удаляет ресурс """

    EntityResource.objects.remove(entity, request.POST.get('resource', ''), provider=provider)
    return HttpResponse('ok')
