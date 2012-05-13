# -*- coding:utf-8 -*-
from django.http import HttpResponse

from elements.locations.models import EntityLocation
from elements.utils import check_permissions, entity_post_method
from locations.models import Location

# TODO: allow to create main location
@entity_post_method
@check_permissions
def add_location(request, entity):
    try:
        loc_id = int(request.POST.get('loc_id', ''))
        location = Location.objects.get(id=loc_id)
    except ValueError, Location.DoesNotExist:
        return HttpResponse(u'Местоположение указано неверно')

    EntityLocation.objects.add(entity, location, {'is_main': False})
    return HttpResponse('ok')

@entity_post_method
@check_permissions
def remove_location(request, entity):
    try:
        loc_id = int(request.POST.get('loc_id', ''))
        location = Location.objects.get(id=loc_id)
    except ValueError, Location.DoesNotExist:
        return HttpResponse(u'Местоположение указано неверно')

    EntityLocation.objects.remove(entity, location)
    return HttpResponse('ok')
