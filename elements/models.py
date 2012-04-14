# -*- coding:utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from locations.models import Location

class BaseEntityPropertyManager(models.Manager):
    def for_entity(self, entity):
        content_type = ContentType.objects.get_for_model(type(entity))
        return self.filter(content_type=content_type, entity_id=entity.id)

class BaseEntityProperty(models.Model):
    content_type = models.ForeignKey(ContentType)
    entity_id = models.PositiveIntegerField()
    entity = generic.GenericForeignKey('content_type', 'entity_id')

    time = models.DateTimeField(auto_now=True, db_index=True)

    objects = BaseEntityPropertyManager()

    class Meta:
        abstract = True

# TODO: add subcategories (?)
# (name, title)
RESOURCE_CHOICES = (
    ('money', u'Деньги'), #u'Возможность оказать финансовую помощь'),
    ('transport', u'Транспорт'), #u'Возможность предоставить автомобиль, автобус, ...'),
    ('time', u'Время'), #u'Возможность самому принять активное участие'),
    ('printing', u'Печать'), #u'Наличие принтера, доступ к типографии, ...'),
    ('premises', u'Помещение'), #u'Ресторан, клуб, спортзал, ...'),
    ('food', u'Общественное питание'), #u'Поставка продуктов, обслуживание обедов'),
    ('auditory', u'Аудитория'), #u'Распространение информации среди своих друзей и читателей'),
    ('people', u'Человеческие ресурсы'), #u'Возможность предоставить волонтеров или наемных рабочих со скидкой'),
    ('organization', u'Представительство в организации'), #u'Руководитель общественного движения, ...'),
    ('authority', u'Представительство во власти'), #u'Муниципальный депутат, полицейский, ...'),
    #('other', u'Другое', u''),
)

# TODO: ability to add text, describing resources + custom resources (in case of other)
class EntityResource(BaseEntityProperty):
    resource = models.CharField(u'Ресурс', max_length=20, choices=RESOURCE_CHOICES, db_index=True)
    text = models.CharField(max_length=200, blank=True) # TODO: depricate

    class Meta:
        unique_together = ('content_type', 'entity_id', 'resource')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.resource)

class EntityLocationManager(models.Manager):
    def for_entity(self, entity):
        content_type = ContentType.objects.get_for_model(type(entity))
        entity_locations = list(self.filter(content_type=content_type, entity_id=entity.id))

        loc_ids = [el.location_id for el in entity_locations]
        locations = Location.objects.filter(id__in=loc_ids).select_related('region', 'district')
        locations_by_id = dict((loc.id, loc) for loc in locations)

        for el in entity_locations:
            el.location = locations_by_id[el.location_id]

        return entity_locations

class EntityLocation(BaseEntityProperty):
    location = models.ForeignKey(Location, related_name='entities')

    objects = EntityLocationManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'location')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.location)
