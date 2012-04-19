# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models

from locations.models import Location

class BaseEntityProperty(models.Model):
    content_type = models.ForeignKey(ContentType)
    entity_id = models.PositiveIntegerField()
    entity = generic.GenericForeignKey('content_type', 'entity_id')

    time = models.DateTimeField(auto_now=True, db_index=True)

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

class EntityResourceManager(models.Manager):
    def update_entity_resources(self, entity, resources):
        # TODO: drop it
        #content_type = ContentType.objects.get_for_model(type(entity))
        #entity_resources = list(self.filter(content_type=content_type, entity_id=entity.id))
        entity_resources = list(entity.resources.all())

        new_resources = set(resources) - set(er.resource for er in entity_resources)
        for er in entity_resources:
            if er.resource not in resources:
                er.delete()

        self.bulk_create([EntityResource(entity=entity, resource=resource) for resource in new_resources])

    def get_for(self, model, ids):
        """ Return {id: [resources]} """
        res = {}
        for id, resource in self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'resource'):
            res.setdefault(id, []).append(resource)
        return res

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
    ('observer', u'Опыт наблюдения на выборах'),
)

class EntitySkillManager(models.Manager):
    def update_entity_skills(self, entity, skills):
        entity_skills = list(entity.skills.all())

        new_skills = set(skills) - set(es.skill for es in entity_skills)
        for es in entity_skills:
            if es.skill not in skills:
                es.delete()

        self.bulk_create([EntitySkill(entity=entity, skill=skill) for skill in new_skills])

    def get_for(self, model, ids):
        """ Return {id: [skills]} """
        res = {}
        for id, skill in self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'skill'):
            res.setdefault(id, []).append(skill)
        return res

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

    # TODO: include data from lower levels
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

class EntityFollowerManager(models.Manager):
    def get_for(self, model, ids):
        """ Return {id: {'count': count, 'top_followers': [top_n_followers]}} """
        followers_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'follower'))

        followers_points = Profile.objects.filter(id__in=[f_id for id, f_id in followers_data]) \
                .values_list('id', 'points')

        res = {}
        for id in ids:
            entity_followers = filter(lambda e_id, f_id: e_id==id, followers_data)
            top_followers_points = sorted(entity_followers,
                    key=lambda f: f[1], reverse=True)[:settings.TOP_FOLLOWERS_COUNT]
            res[id] = {
                'count': len(entity_followers),
                'top_followers': map(lambda f: f[0], top_followers_points),
            }
        return res

class EntityFollower(BaseEntityProperty):
    follower = models.ForeignKey(Profile, related_name='followed_entities')

    objects = EntityFollowerManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'follower')

    def __unicode__(self):
        return unicode(self.follower) + ' follows ' + unicode(self.entity)

# TODO: add search method
class BaseEntityManager(models.Manager):
    def info_for(self, ids):
        """ Get dict {id: info} for model. Use and update cache if needed. """
        cache_prefix = self.model.cache_prefix
        cached_entities = cache.get_many([cache_prefix+str(id) for id in ids])

        cached_ids = []
        res = {}
        for key, entity in cached_entities.iteritems():
            id = int(key[len(cache_prefix):])
            cached_ids.append(id)
            res[id] = entity

        other_ids = set(ids) - set(cached_ids)
        if len(other_ids) > 0:
            other_res = dict((id, {}) for id in other_ids)

            if 'resources' in self.model.features:
                resources_data = EntityResource.objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id]['resources'] = resources_data.get(id, [])

            if 'skills' in self.model.features:
                skills_data = EntitySkills.objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id]['skills'] = skills_data.get(id, [])

            if 'followers' in self.model.features:
                followers_data = EntityFollower.objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id]['followers'] = followers_data[id]['top_followers']
                    other_res[id]['followers_count'] = followers_data[id]['count']

            self.get_info(other_res)

            for id, info in other_res.iteritems():
                cache_res[cache_prefix+str(id)] = info

            cache.set_many(cache_res, 60) # TODO: specify time as a model attribute

            res.update(other_res)

        return res

    def get_info(self, data):
        """ Take {id: info} filled with features data and add the rest information """
        raise NotImplemented

    def for_location(self, location, start=0, limit=None, sort_by='points'):
        """ Return sorted list of entity ids """
        raise NotImplemented

# TODO: add admins, complaints, files/images
# TODO: reset cache key on changing any of related data or save/delete (base method/decorator)
class BaseEntityModel(models.Model):
    points = models.IntegerField(default=0) # used for sorting entities

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)
    add_time = models.DateTimeField(auto_now_add=True, null=True, db_index=True)

    objects = BaseManager()

    cache_prefix = ''
    features = [] # 'skills', 'resources', 'followers', # TODO: 'location' (?),  'complaints', 'admins'

    class Meta:
        abstract = True

    def cache_key(self):
        return self.cache_prefix + str(self.id)

    def info(self):
        return self.objects.info_for([self.id])

    # TODO: recalculate these points on save or in celery (?)
    def calc_points(self):
        """ Return points using entity info """
        raise NotImplemented

@reset_cache
def update_resources(self, resources):
    EntityResource.objects.update_entity_resources(self, resources)

@reset_cache
def update_skills(self, skills):
    EntitySkill.objects.update_entity_resources(self, skills)

def entity_class(name, features):
    attr = {'features': features}

    if 'resources' in features:
        attr['resources'] = generic.GenericRelation(EntityResource, object_id_field='entity_id')
        attr['update_resources'] = update_resources

    if 'skills' in features:
        attr['skills'] = generic.GenericRelation(EntitySkill, object_id_field='entity_id')
        attr['update_skills'] = update_skills

    if 'followers' in features:
        attr['followers'] = generic.GenericRelation(EntityFollower, object_id_field='entity_id')

    model = type(name, (BaseEntityModel,), attrs)

    # TODO: is it correct?
    model.save = reset_cache(model.save)
    model.delete = reset_cache(model.delete)

    return model
