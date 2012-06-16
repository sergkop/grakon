# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField
from tools.tasks.models import Task
from users.models import Profile

class IdeaManager(BaseEntityManager):
    def get_info(self, data, ids):
        for id in ids:
            data[id]['projects'] = {'ids': []}

        from tools.projects.models import ProjectIdeas
        pi_data = ProjectIdeas.objects.filter(idea__in=ids).values_list('project', 'idea')
        for proj_id, id in pi_data:
            data[id]['projects']['ids'].append(proj_id)

        for id in ids:
            data[id]['projects']['count'] = len(data[id]['projects']['ids'])

    def get_related_info(self, data, ids):
        provider_ids = set(p_id for id in ids for p_id in data[id]['resources'])
        if 'none' in provider_ids:
            provider_ids.remove('none')

        providers_info = Profile.objects.info_for(provider_ids, related=False)
        for id in ids:
            for p_id in data[id]['resources']:
                if p_id != 'none':
                    data[id]['resources'][p_id]['provider'] = providers_info[p_id]

        from tools.projects.models import Project
        proj_ids = [proj_id for id in ids for proj_id in data[id]['projects']['ids']]
        proj_info = Project.objects.info_for(proj_ids, related=False)

        for id in ids:
            data[id]['projects']['entities'] = [proj_info[proj_id] for proj_id in data[id]['projects']['ids']]

# TODO: reset cache for related projects on save (and vice versa)
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

    disqus_category = 'ideas'

    def disqus_id(self):
        return 'idea/' + str(self.id)

    def disqus_url(self):
        return self.get_absolute_url()

    @models.permalink
    def get_absolute_url(self):
        return ('idea', [self.id])

    def __unicode__(self):
        return self.title
