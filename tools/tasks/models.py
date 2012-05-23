# -*- coding:utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField
from posts.models import EntityPost

class TaskManager(BaseEntityManager):
    def get_info(self, data, ids):
        pass

# TODO: introduce choices for types
@entity_class(['locations', 'participants', 'posts'])
class Task(BaseEntityModel):
    title = models.CharField(u'Формулировка', max_length=250)
    about = HTMLField(u'Описание', blank=True)

    objects = TaskManager()

    entity_name = 'tasks'
    entity_title = u'Задачи'
    cache_prefix = 'tasks/'
    table_header = 'tasks/table_header.html'
    table_line = 'tasks/table_line.html'
    table_cap = 'tasks/table_cap.html'

    roles = ['admin', 'follower']

    @models.permalink
    def get_absolute_url(self):
        return ('task', [self.id])

    def __unicode__(self):
        return self.title
