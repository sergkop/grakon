# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField

class EventManager(BaseEntityManager):
    pass

# TODO: add event type
@entity_class(['followers', 'locations', 'admins'])
class Event(BaseEntityModel):
    title = models.CharField(u'Название', max_length=150)
    description = HTMLField(u'Описание', blank=True)
    place = models.CharField(u'Место проведения', max_length=250)
    event_time = models.DateTimeField(u'Время проведения', db_index=True)

    objects = EventManager()

    entity_name = 'events'
    entity_title = u'Мероприятия'
    cache_prefix = 'event/'
    table_header = 'events/table_header.html'
    table_line = 'events/table_line.html'
    table_cap = 'events/table_cap.html'

    @models.permalink
    def get_absolute_url(self):
        return ('event', [self.id])

    def __unicode__(self):
        return self.title
