# -*- coding:utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

from grakon.utils import authenticated_ajax_post

from elements.models import EntityFollower

def get_entity(post_data):
    """ Shortcut returning entity or None for form data """
    try:
        ct_id = int(post_data.get('ct', ''))
    except ValueError:
        return

    try:
        id = int(post_data.get('id', ''))
    except ValueError:
        return

    try:
        content_type = ContentType.objects.get_for_id(ct_id)
    except ContentType.DoesNotExist: # TODO: is the error correct?
        return

    model = content_type.model_class()
    try:
        return model.objects.get(id=id)
    except model.DoesNotExist: # TODO: is the error correct?
        return

@authenticated_ajax_post
def add_follower(request):
    entity = get_entity(request.POST)
    if not entity:
        return HttpResponse(u'Запись указана неверно')

    EntityFollower.objects.add_follower(entity, request.profile)
    # TODO: send letter to user if he is followed (control by settings)
    return HttpResponse('ok')

@authenticated_ajax_post
def remove_follower(request):
    entity = get_entity(request.POST)
    if not entity:
        return HttpResponse(u'Запись указана неверно')

    EntityFollower.objects.remove_follower(entity, request.profile)
    return HttpResponse('ok')

# TODO: generalize to for all entities, check that user has rights for update (his profile or he is admin)
@authenticated_ajax_post
def update_resources(request):
    # TODO: get entity, return error on fail
    request.profile.update_resources(request.POST.getlist('value[]', None))
    return HttpResponse('ok')
