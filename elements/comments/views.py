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
            return HttpResponse(u'Родительский комментарий указан неверно')

        # TODO: also check content type
        if parent_comment.entity_id != entity.id:
            return HttpResponse(u'На этот комментарий ответить нельзя')
    else:
        parent_comment = None
        parent_id = None

    text = request.POST.get('comment', '').strip()
    if text == '':
        return HttpResponse(u'Комментарий должен быть непустымы')

    EntityComment.objects.add(entity, request.profile, text, parent_id)

    return HttpResponse('ok')

@entity_post_method
def remove_comment(request, entity):
    try:
        comment_id = request.POST.get('comment_id', '')
        comment = EntityComment.objects.get(id=comment_id)
    except ValueError, EntityComment.DoesNotExist:
        return HttpResponse(u'Комментарий указан неверно')

    if comment.person_id != request.profile.id:
        return HttpResponse(u'Вы не можете удалить этот комментарий')

    # TODO: what happens when comment has children?

    EntityComment.objects.remove(entity, request.profile, comment_id)

    return HttpResponse('ok')
