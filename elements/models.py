# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.db.models import Q

from elements.utils import reset_cache
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

    # Skills
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

RESOURCE_DICT = dict((name, title) for name, title in RESOURCE_CHOICES)

class EntityResourceManager(models.Manager):
    def update_entity_resources(self, entity, resources):
        # TODO: this code doesn't work any more
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
            res.setdefault(id, []).append({'name': resource, 'title': RESOURCE_DICT[resource]})
        return res

# TODO: ability to add text, describing resources + custom resources (in case of other)
class EntityResource(BaseEntityProperty):
    resource = models.CharField(u'Ресурс', max_length=20, choices=RESOURCE_CHOICES, db_index=True)

    objects = EntityResourceManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'resource')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.resource)

class EntityLocationManager(models.Manager):
    def get_for(self, model, ids):
        """ Return {id: {'locations': loc_ids, 'main_location': loc_id_or_None}} """
        locations_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'location', 'is_main'))

        res = {}
        for id in ids:
            entity_locations = filter(lambda el: el[0]==id, locations_data)
            res[id] = {'locations': map(lambda el: el[1], entity_locations)}

            main_locations = filter(lambda el: el[2], entity_locations)
            res[id]['main_location'] = main_locations[0][1] if main_locations else None
        return res

# TODO: reset cache on save()/delete() (here and in other models)
class EntityLocation(BaseEntityProperty):
    location = models.ForeignKey(Location, related_name='entities')
    is_main = models.BooleanField(default=False, db_index=True)

    objects = EntityLocationManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'location')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.location)

class EntityFollowerManager(models.Manager):
    def get_for(self, model, ids):
        """ Return {id: {'count': count, 'top_followers': [top_followers_ids]}} """
        followers_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'follower'))

        from users.models import Profile
        followers_points = Profile.objects.filter(id__in=[f_id for id, f_id in followers_data]) \
                .values_list('id', 'points')

        res = {}
        for id in ids:
            entity_followers = filter(lambda f: f[0]==id, followers_data)
            top_followers_points = sorted(entity_followers,
                    key=lambda f: f[1], reverse=True)[:settings.TOP_FOLLOWERS_COUNT]
            res[id] = {
                'count': len(entity_followers),
                'top_followers': map(lambda f: f[0], top_followers_points),
            }
        return res

class EntityFollower(BaseEntityProperty):
    follower = models.ForeignKey('users.Profile', related_name='followed_entities')

    objects = EntityFollowerManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'follower')

    def __unicode__(self):
        return unicode(self.follower) + ' follows ' + unicode(self.entity)

# TODO: add search method
class BaseEntityManager(models.Manager):
    def info_for(self, ids, related=True):
        """
        Get dict {id: info} for model. Use and update cache if needed.
        If related is True, list of info is returned instead of ids.
        """
        features = self.model.features
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

            if 'resources' in features:
                resources_data = EntityResource.objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id]['resources'] = resources_data.get(id, [])

            if 'followers' in features:
                followers_data = EntityFollower.objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id]['followers'] = followers_data[id]['top_followers']
                    other_res[id]['followers_count'] = followers_data[id]['count']

            if 'locations' in features:
                locations_data = EntityLocation.objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id]['locations'] = locations_data[id]['locations']
                    other_res[id]['main_location'] = locations_data[id]['main_location']

            # Add custom model info
            self.get_info(other_res)

            cache_res = dict((cache_prefix+str(id), other_res[id]) for id in other_res)
            cache.set_many(cache_res, 60) # TODO: specify time as a model attribute

            res.update(other_res)

        if related:
            if 'followers' in features:
                from users.models import Profile
                followers_ids = set(f_id for id in ids for f_id in res[id]['followers'])
                followers_info = Profile.objects.info_for(followers_ids, related=False)

                for id in ids:
                    res[id]['followers'] = [followers_info[f_id] for f_id in res[id]['followers']
                            if f_id in followers_info]

            if 'locations' in features:
                loc_ids = set(loc_id for id in ids for loc_id in res[id]['locations'])
                locs_info = Location.objects.info_for(loc_ids, related=False)

                for id in ids:
                    res[id]['locations'] = [locs_info[loc_id] for loc_id in res[id]['locations']]
                    res[id]['main_location'] = locs_info[res[id]['main_location']] if res[id]['main_location'] else None

        return res

    def get_info(self, data):
        """ Take {id: info} filled with features data and add the rest information """
        raise NotImplemented

    # TODO: take is_main into account
    # TODO: cache it (at least for data for side panels) - in Location
    def for_location(self, location, start=0, limit=None, sort_by=('-points',)):
        """ Return sorted list of entities ids """
        if location.is_country():
            # Special processing to minify entity_query
            entity_query = Q()
        else:
            loc_query = Q(location__id=location.id)

            field = location.children_query_field()
            if field:
                loc_query |= Q(**{'location__'+field: location.id})

            entity_ids = list(EntityLocation.objects.filter(
                    content_type=ContentType.objects.get_for_model(self.model)) \
                    .filter(loc_query).values_list('entity_id', flat=True))

            # TODO: what happens when the list of ids is too long (for the next query)?
            entity_query = Q(id__in=entity_ids)

        ids = self.filter(entity_query).order_by(*sort_by).values_list('id', flat=True)
        if limit is None:
            ids = ids[start:]
        else:
            ids = ids[start:start+limit]

        return ids

# TODO: add admins, complaints, files/images
# TODO: reset cache key on changing any of related data or save/delete (base method/decorator)
class BaseEntityModel(models.Model):
    points = models.IntegerField(u'Очки', default=0) # used for sorting entities

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)
    add_time = models.DateTimeField(auto_now_add=True, null=True, db_index=True)

    objects = BaseEntityManager()

    cache_prefix = ''
    features = [] # 'resources', 'followers', # TODO: 'location' (?),  'complaints', 'admins'

    class Meta:
        abstract = True

    def cache_key(self):
        return self.cache_prefix + str(self.id)

    def info(self, related=True):
        return type(self).objects.info_for([self.id], related)[self.id]

    # TODO: recalculate these points on save or in celery (?)
    def calc_points(self):
        """ Return points using entity info """
        raise NotImplemented

    @reset_cache
    def save(self, *args, **kwargs):
        return super(BaseEntityModel, self).save(*args, **kwargs)

    @reset_cache
    def delete(self, *args, **kwargs):
        return super(BaseEntityModel, self).delete(*args, **kwargs)

@reset_cache
def update_resources(self, resources):
    EntityResource.objects.update_entity_resources(self, resources)

def entity_class(model, features):
    """ Call it right after model definition """
    attrs = {'features': features}

    if 'resources' in features:
        attrs['resources'] = generic.GenericRelation(EntityResource, object_id_field='entity_id')
        attrs['update_resources'] = update_resources

    if 'followers' in features:
        attrs['followers'] = generic.GenericRelation(EntityFollower, object_id_field='entity_id')

    if 'locations' in features:
        attrs['locations'] = generic.GenericRelation(EntityLocation, object_id_field='entity_id')

    for attr, value in attrs.iteritems():
        setattr(model, attr, value)
