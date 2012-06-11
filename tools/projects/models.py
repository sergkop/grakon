# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField

class ProjectManager(BaseEntityManager):
    def get_info(self, data, ids):
        pass

@entity_class(['locations', 'participants'])
class Project(BaseEntityModel):
    title = models.CharField(u'Формулировка', max_length=250)
    deadline = models.CharField(u'Дедлайн', max_length=250, blank=True)
    goals = HTMLField(u'Цели')
    stages = HTMLField(u'Этапы', blank=True)
    about = HTMLField(u'Суть')
    team = HTMLField(u'Кто уже помог проекту', blank=True)

    objects = ProjectManager()

    entity_name = 'projects'
    entity_title = u'Проекты'
    cache_prefix = 'projects/'
    editable_fields = ['title', 'deadline', 'goals', 'stages', 'about', 'team']

    roles = ['admin', 'follower']

    disqus_category = 'projects'

    def disqus_id(self):
        return 'project/' + str(self.id)

    def disqus_url(self):
        return reverse('project_wall', args=[self.id])

    @models.permalink
    def get_absolute_url(self):
        return ('project', [self.id])

    def __unicode__(self):
        return self.title

class ProjectIdeas(models.Model):
    project = models.ForeignKey(Project, related_name='ideas')
    idea = models.ForeignKey('ideas.Idea', related_name='projects')

    class Meta:
        unique_together = ('project', 'idea')
