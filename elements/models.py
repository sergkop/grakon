# -*- coding:utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
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

class EntityResourceManager(BaseEntityPropertyManager):
    def update_entity_resources(self, entity, resources):
        content_type = ContentType.objects.get_for_model(type(entity))

        entity_resources = list(self.filter(content_type=content_type, entity_id=entity.id))

        new_resources = set(resources) - set(er.resource for er in entity_resources)
        for er in entity_resources:
            if er.resource not in resources:
                er.delete()

        self.bulk_create([EntityResource(entity=entity, resource=resource) for resource in new_resources])

# TODO: ability to add text, describing resources + custom resources (in case of other)
class EntityResource(BaseEntityProperty):
    resource = models.CharField(u'Ресурс', max_length=20, choices=RESOURCE_CHOICES, db_index=True)

    objects = EntityResourceManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'resource')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.resource)

SKILL_CHOICES = (
    ('lawyer', u'Юридическая помощь'),
    ('programmer', u'Программирование'),
    ('design', u'Дизайн'),
    ('copywriting', u'Написание текстов'),
    #('creative', u'Креатив'), # TODO: improve
    ('organizator', u'Организаторские навыки'),
    #('', u'Физическая сила'), # TODO: improve
    ('musician', u'Музыкальные навыки'),
    ('photographer', u'Фотография'),
    ('journalist', u'Журналистские навыки'),
    ('observer', u'опыт наблюдения на выборах'),
)

class EntitySkillManager(BaseEntityPropertyManager):
    def update_entity_resources(self, entity, skills):
        content_type = ContentType.objects.get_for_model(type(entity))

        entity_skills = list(self.filter(content_type=content_type, entity_id=entity.id))

        new_skills = set(skills) - set(es.skill for es in entity_skills)
        for es in entity_skills:
            if es.skill not in skills:
                es.delete()

        self.bulk_create([EntitySkill(entity=entity, skill=skill) for skill in new_skills])

class EntitySkill(BaseEntityProperty):
    skill = models.CharField(u'Навык', max_length=20, choices=SKILL_CHOICES, db_index=True)

    objects = EntitySkillManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'skill')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.skill)

class EntityLocationManager(models.Manager):
    # TODO: cache it
    def for_entity(self, entity):
        content_type = ContentType.objects.get_for_model(type(entity))
        entity_locations = list(self.filter(content_type=content_type, entity_id=entity.id))

        loc_ids = [el.location_id for el in entity_locations]
        locations = Location.objects.filter(id__in=loc_ids).select_related('region', 'district')
        locations_by_id = dict((loc.id, loc) for loc in locations)

        for el in entity_locations:
            el.location = locations_by_id[el.location_id]

        return entity_locations

    # TODO: include data from higher and lower levels
    def for_location(self, loc_id):
        res = {} # {ct_id: [entity_ids]}
        for ct_id, entity_id in self.filter(location__id=loc_id).values_list('content_type', 'entity_id'):
            res.setdefault(ct_id, []).append(entity_id)
        return res

    # TODO: do we need it?
    # TODO: shortcut method for it in Location
    # TODO: don't cache if entity_type is given? simplify result?
    def for_locations(self, loc_ids, entity_type=None):
        """ Get all entities of given type (all if not given) at the given location """
        cached_entities = cache.get_many(['loc_entities/'+str(loc_id) for loc_id in loc_ids])

        cached_loc_ids = [int(key.split('/')[1]) for key in cached_entities.keys()]
        res = dict((int(key.split('/')[1]), entity) for key, entity in cached_entities.iteritems())

        other_loc_ids = set(loc_ids) - set(cached_loc_ids)
        if len(other_loc_ids) > 0:
            queryset = self.filter(location__in=other_loc_ids)
            if entity_type:
                content_type = ContentType.objects.get_for_model(entity_type)
                queryset = queryset.filter(content_type=content_type)

            # Get entities content types and ids
            entity_locations = {} # {loc_id: {ct_id: [entity_ids]}}
            for ct_id, entity_id, loc_id in queryset.values_list('content_type', 'entity_id', 'location'):
                entity_locations.setdefault(loc_id, {}).setdefault(ct_id, []).append(entity_id)

            # Get all entities ids by content type
            entity_ids_by_ct = {} # {ct_id: [entity_ids]}
            for el in entity_locations.values():
                for ct_id, entity_ids in el.iteritems():
                    entity_ids_by_ct.setdefault(ct_id, []).extend(entity_ids)

            # Retrieve data from db
            entities_by_ct = {} # {ct_id: [entities]}
            for ct_id, entity_ids in entity_ids_by_ct.iteritems():
                model = ContentType.objects.get_for_id(ct_id).model_class()
                entities_by_ct[ct_id] = dict(
                        (entity.id, entity) for entity in model.objects.filter(id__in=entity_ids))

            cache_res = {}
            for loc_id in entity_locations:
                for ct_id in entity_locations[loc_id]:
                    for entity_id in entity_locations[loc_id][ct_id]:
                        res.setdefault(loc_id, {}).setdefault(ct_id, {})[entity_id] = \
                                entities_by_ct[ct_id][entity_id]
                        cache_res.setdefault('loc_entities/'+str(loc_id), {}).setdefault(ct_id, {})[entity_id] = \
                                entities_by_ct[ct_id][entity_id]

            cache.set_many(cache_res, 30)

        return res

# TODO: reset cache on save()/delete() (here and in other models)
class EntityLocation(BaseEntityProperty):
    location = models.ForeignKey(Location, related_name='entities')

    objects = EntityLocationManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'location')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.location)
