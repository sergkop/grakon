# -*- coding:utf-8 -*-
from django.http import HttpResponse

from elements.models import EntityFollower, EntityLocation
from elements.utils import check_permissions, entity_post_method
from locations.models import Location
from users.models import Profile

@entity_post_method
def add_follower(request, entity):
    EntityFollower.objects.add(entity, request.profile)
    # TODO: send letter to user if he is followed (control by settings)
    return HttpResponse('ok')

@entity_post_method
def remove_follower(request, entity):
    EntityFollower.objects.remove(entity, request.profile)
    return HttpResponse('ok')

#@entity_post_method
#@check_permissions
#def update_resources(request, entity):
#    EntityResource.objects.update(entity, request.POST.getlist('value[]', None))
#    return HttpResponse('ok')

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

"""
@entity_post_method
def add_post(request, entity):
    EntityPost.objects.add(entity, request.profile, content, url, opinion)
    return HttpResponse('ok')
"""
