# -*- coding:utf-8 -*-
from django.http import HttpResponse

from elements.comments.models import EntityComment
from elements.utils import entity_post_method

@entity_post_method
def add_comment(request, entity):
    parent_id = request.POST.get('parent', '')

    if parent_id != '':
        try:
            parent_id = int(parent_id)
            parent_comment = EntityComment.objects.get(id=parent_id)
        except ValueError, EntityComment.DoesNotExist:
            return HttpResponse(u'На этот комментарий ответить нельзя')

        if parent_comment.entity_id != entity.id:
            return HttpResponse(u'На этот комментарий ответить нельзя')
    else:
        parent_comment = None

    return HttpResponse('ok')
