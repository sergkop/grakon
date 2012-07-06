# -*- coding:utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField

class TaskManager(BaseEntityManager):
    def get_info(self, data, ids):
        # Get related ideas
        for id in ids:
            data[id]['ideas'] = {'ids': []}

        from tools.ideas.models import Idea
        ideas_data = Idea.objects.filter(task__in=ids).values_list('id', 'task')
        for idea_id, id in ideas_data:
            data[id]['ideas']['ids'].append(idea_id)

        for id in ids:
            data[id]['ideas']['count'] = len(data[id]['ideas']['ids'])

    def get_related_info(self, data, ids):
        # Get ideas info
        ideas_ids = [idea_id for id in ids for idea_id in data[id]['ideas']['ids']]
        from tools.ideas.models import Idea
        ideas_info = Idea.objects.info_for(ideas_ids, related=False)

        for id in ids:
            data[id]['ideas']['entities'] = [ideas_info[idea_id] for idea_id in data[id]['ideas']['ids']]

        # Get resources data
        for id in ids:
            data[id]['resources'] = {
                'count': len(set(provider_id for idea_info in data[id]['ideas']['entities'] for provider_id in idea_info['resources'])),
            }

# TODO: introduce choices for types
@entity_class(['locations', 'participants', 'comments'])
class Task(BaseEntityModel):
    title = models.CharField(u'Формулировка', max_length=250,
            help_text=u'краткая формулировка гражданской задачи в виде вопроса. Лучше всего начать ее со слова "как", например: "как быстро и недорого обустроить свой двор?"')
    about = HTMLField(u'Описание', blank=True)

    objects = TaskManager()

    entity_name = 'tasks'
    entity_title = u'Задачи'
    cache_prefix = 'tasks/'
    editable_fields = ['title', 'about']

    roles = ['admin', 'follower']

    follow_button = {
        'role': 'follower',
        'cancel_msg': u'Вы хотите отписаться от новостей об этой задаче?',
        'cancel_btn': u'Отписаться',
        'cancel_btn_long': u'Отписаться',
        'confirm_msg': u'Вы хотите следить за новыми идеями для этой задачи?',
        'confirm_btn': u'Следить',
        'confirm_btn_long': u'Следить за задачей',
    }

    def calc_rating(self):
        # Number of people provided resources for task ideas
        info = self.info()
        providers = len(set(provider_id for idea_info in info['ideas']['entities'] \
                for provider_id in idea_info['resources']))
        ideas = info['ideas']['count']
        followers = info['participants']['follower']['count']
        return 25*providers + 5*ideas + followers

    @models.permalink
    def get_absolute_url(self):
        return ('task', [self.id])

    def __unicode__(self):
        return self.title
