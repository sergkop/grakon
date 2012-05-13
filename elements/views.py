from django.http import HttpResponse

from elements.utils import check_permissions, entity_post_method

# TODO: depricate or move to resources
#@entity_post_method
#@check_permissions
#def update_resources(request, entity):
#    EntityResource.objects.update(entity, request.POST.getlist('value[]', None))
#    return HttpResponse('ok')
