# -*- coding:utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField

class TaskManager(BaseEntityManager):
    def get_info(self, data, ids):
        from tools.ideas.models import Idea
        ideas_data = Idea.objects.filter(task__in=ids).values_list('id', 'task')

        for id in ids:
            data[id]['ideas'] = {'ids': []}

        for idea_id, id in ideas_data:
            data[id]['ideas']['ids'].append(idea_id)

        for id in ids:
            data[id]['ideas'] = {'count': len(data[id]['ideas']['ids'])}

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
    editable_fields = ['title', 'about']

    roles = ['admin', 'follower']

    disqus_category = 'tasks'

    def disqus_id(self):
        return 'task/' + str(self.id)

    def disqus_url(self):
        return reverse('task_wall', args=[self.id])

    @models.permalink
    def get_absolute_url(self):
        return ('task', [self.id])

    def __unicode__(self):
        return self.title
