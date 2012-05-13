from django.http import HttpResponse

from elements.followers.models import EntityFollower
from elements.utils import entity_post_method

@entity_post_method
def add_follower(request, entity):
    EntityFollower.objects.add(entity, request.profile)
    # TODO: send letter to user if he is followed (control by settings)
    return HttpResponse('ok')

@entity_post_method
def remove_follower(request, entity):
    EntityFollower.objects.remove(entity, request.profile)
    return HttpResponse('ok')
