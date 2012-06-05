# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField
from tools.tasks.models import Task
from users.models import Profile

class IdeaManager(BaseEntityManager):
    def get_related_info(self, data, ids):
        provider_ids = set(p_id for id in ids for p_id in data[id]['resources'])
        if 'none' in provider_ids:
            provider_ids.remove('none')

        providers_info = Profile.objects.info_for(provider_ids, related=False)
        for id in ids:
            for p_id in data[id]['resources']:
                if p_id != 'none':
                    data[id]['resources'][p_id]['provider'] = providers_info[p_id]

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
