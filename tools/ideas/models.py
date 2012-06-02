# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField
from tools.tasks.models import Task

class IdeaManager(BaseEntityManager):
    pass

@entity_class(['participants', 'resources'])
class Idea(BaseEntityModel):
    task = models.ForeignKey(Task, related_name='ideas')
    title = models.CharField(u'Название', max_length=150)
    description = HTMLField(u'Описание', blank=True)

    objects = IdeaManager()

    entity_name = 'ideas'
    entity_title = u'Идеи'
    cache_prefix = 'idea/'
    editable_fields = ['title', 'description']

    roles = ['admin']

    @models.permalink
    def get_absolute_url(self):
        return ('idea', [self.id])

    def __unicode__(self):
        return self.title
