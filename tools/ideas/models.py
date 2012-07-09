# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField
from tools.tasks.models import Task

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

        # Get related tasks
        task_ids = {data[id]['instance']['task_id'] for id in ids}
        tasks_by_id = Task.objects.in_bulk(task_ids)

        for id in ids:
            task = tasks_by_id[data[id]['instance']['task_id']]
            data[id]['task'] = {
                'title': task.title,
                'url': task.get_absolute_url(),
            }

    def get_related_info(self, data, ids):
        from tools.projects.models import Project
        proj_ids = [proj_id for id in ids for proj_id in data[id]['projects']['ids']]
        proj_info = Project.objects.info_for(proj_ids, related=False)

        for id in ids:
            data[id]['projects']['entities'] = [proj_info[proj_id] for proj_id in data[id]['projects']['ids']]

# TODO: reset cache for related projects on save (and vice versa)
@entity_class(['participants', 'resources', 'comments'])
class Idea(BaseEntityModel):
    task = models.ForeignKey(Task, related_name='ideas')
    description = HTMLField(u'Описание', blank=True)

    objects = IdeaManager()

    entity_name = 'ideas'
    entity_title = u'Идеи'
    cache_prefix = 'idea/'
    editable_fields = ['description']

    roles = ['admin']

    def calc_rating(self):
        # Number of people provided resources for idea
        return len(self.info()['resources'])

    @models.permalink
    def get_absolute_url(self):
        return ('idea', [self.id])

    def __unicode__(self):
        return 'Idea for task "%s"' % self.task.title
