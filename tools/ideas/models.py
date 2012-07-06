# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField
from notifications.models import NotificationType, register_notification
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
    title = models.CharField(u'Название', max_length=150)
    description = HTMLField(u'Описание', blank=True)

    objects = IdeaManager()

    entity_name = 'ideas'
    entity_title = u'Идеи'
    cache_prefix = 'idea/'
    editable_fields = ['title', 'description']

    roles = ['admin']

    def calc_rating(self):
        # Number of people provided resources for idea
        return len(self.info()['resources'])

    @models.permalink
    def get_absolute_url(self):
        return ('idea', [self.id])

    def __unicode__(self):
        return self.title

@register_notification
class NewIdeaNotification(NotificationType):
    """ data = idea_id """
    name = 'new_idea'
    template = 'notifications/new_idea.html'

    @classmethod
    def recipients(cls, data):
        idea_id = data
        idea = Idea.objects.select_related('task').get(id=idea_id)

        idea_info = idea.info(related=False)
        task_info = idea.task.info(related=True)

        res = []

        # Creators of idea
        res += [idea_admin['id'] for idea_info in task_info['ideas']['entities']
                for idea_admin in idea_info['participants']['admin']['entities']]

        # Providers of idea resources
        res += [provider for idea_info in task_info['ideas']['entities']
                for provider in idea_info['resources'].keys()]

        # Creator of task
        res += [e['id'] for e in task_info['participants']['admin']['entities']]

        # Followers of task
        res += [e['id'] for e in task_info['participants']['follower']['entities']]

        # Exclude creator of the idea
        res = set(res) - set([idea_info['participants']['admin']['entities'][0]['id']])

        return res

    @classmethod
    def context(cls, data):
        idea_id = data
        idea = Idea.objects.select_related('task').get(id=idea_id)
        return {'idea': idea, 'task': idea.task}
