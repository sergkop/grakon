# -*- coding:utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

from grakon.utils import authenticated_ajax_post

from elements.models import EntityFollower, EntityLocation
from locations.models import Location

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

@entity_post_method
def add_follower(request, entity):
    EntityFollower.objects.add(entity, request.profile)
    # TODO: send letter to user if he is followed (control by settings)
    return HttpResponse('ok')

@entity_post_method
def remove_follower(request, entity):
    EntityFollower.objects.remove(entity, request.profile)
    return HttpResponse('ok')

@entity_post_method
def update_resources(request, entity):
    # TODO: generalize for all entities
    # TODO: check that user has rights for update (his profile or he is admin)
    request.profile.update_resources(request.POST.getlist('value[]', None))
    return HttpResponse('ok')

@entity_post_method
def add_location(request, entity):
    try:
        loc_id = int(request.POST.get('loc_id', ''))
        location = Location.objects.get(id=loc_id)
    except ValueError, Location.DoesNotExist:
        return HttpResponse(u'Местоположение указано неверно')

    # TODO: check that user has rights for update (his profile or he is admin)
    EntityLocation.objects.add(entity, location, is_main=False)
    return HttpResponse('ok')
