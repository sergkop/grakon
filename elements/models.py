# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.db.models import Q

from elements.utils import reset_cache
from locations.models import Location

class BaseEntityManager(models.Manager):
    def get_related_info(self, data, ids):
        pass

class BaseEntityProperty(models.Model):
    content_type = models.ForeignKey(ContentType)
    entity_id = models.PositiveIntegerField(db_index=True)
    entity = generic.GenericForeignKey('content_type', 'entity_id')

    time = models.DateTimeField(auto_now=True, db_index=True)

    objects = BaseEntityManager()

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

class EntityResourceManager(BaseEntityManager):
    # TODO: reset cache
    # TODO: check if entity model has resources feature
    def update_entity_resources(self, entity, resources):
        entity_resources = list(type(entity).resources.all())

        new_resources = set(resources) - set(er.resource for er in entity_resources)
        for er in entity_resources:
            if er.resource not in resources:
                er.delete()

        self.bulk_create([EntityResource(entity=entity, resource=resource) for resource in new_resources])

    def get_for(self, model, ids):
        """ Return {id: [resources]} """
        res = dict((id, []) for id in ids)
        for id, resource in self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'resource'):
            res[id].append({'name': resource, 'title': RESOURCE_DICT[resource]})
        return res

# TODO: ability to add text, describing resources + custom resources (in case of other)
class EntityResource(BaseEntityProperty):
    resource = models.CharField(u'Ресурс', max_length=20, choices=RESOURCE_CHOICES, db_index=True)

    objects = EntityResourceManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'resource')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.resource)

class EntityLocationManager(BaseEntityManager):
    def get_for(self, model, ids):
        """ Return {id: {'ids': loc_ids, 'main_id': loc_id_or_None}} """
        locations_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'location', 'is_main'))

        res = {}
        for id in ids:
            entity_locations = filter(lambda el: el[0]==id, locations_data)
            res[id] = {'ids': map(lambda el: el[1], entity_locations)}

            main_locations = filter(lambda el: el[2], entity_locations)
            res[id]['main_id'] = main_locations[0][1] if main_locations else None
        return res

    def get_related_info(self, data, ids):
        loc_ids = set(loc_id for id in ids for loc_id in data[id]['locations']['ids'])
        locs_info = Location.objects.info_for(loc_ids, related=False)

        for id in ids:
            data[id]['locations']['locations'] = [locs_info[loc_id] for loc_id in data[id]['locations']['ids']]
            data[id]['locations']['main'] = locs_info[data[id]['locations']['main_id']] \
                    if data[id]['locations']['main_id'] else None

    def add(self, entity, location, is_main=False):
        if 'locations' not in type(entity).features:
            return

        self.get_or_create(content_type=ContentType.objects.get_for_model(entity),
                entity_id=entity.id, location=location, defaults={'is_main': is_main})
        entity.clear_cache()
        location.clear_cache()

    def remove(self, entity, location):
        if 'locations' not in type(entity).features:
            return

        self.filter(content_type=ContentType.objects.get_for_model(entity),
                entity_id=entity.id, location=location).delete()
        entity.clear_cache()
        location.clear_cache()

# TODO: some models may need only one location (?)
# TODO: reset cache on save()/delete() (here and in other models)
class EntityLocation(BaseEntityProperty):
    location = models.ForeignKey(Location, related_name='entities')
    is_main = models.BooleanField(default=False, db_index=True)

    objects = EntityLocationManager()

    class Meta:
        unique_together = ('content_type', 'entity_id', 'location')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.location)

class EntityFollowerManager(BaseEntityManager):
    def get_for(self, model, ids):
        """ Return followers data {id: {'count': count, 'ids': [top_followers_ids]}} """
        followers_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'follower'))

        from users.models import Profile
        followers_points = Profile.objects.filter(id__in=map(lambda f: f[1], followers_data)) \
                .values_list('id', 'points')

        res = {}
        for id in ids:
            f_ids = map(lambda fd: fd[1], filter(lambda f: f[0]==id, followers_data))
            top_followers_points = sorted(filter(lambda f: f[0] in f_ids, followers_points),
                    key=lambda f: f[1], reverse=True)[:settings.TOP_FOLLOWERS_COUNT]
            res[id] = {
                'count': len(f_ids),
                'ids': map(lambda f: f[0], top_followers_points),
            }
        return res

    def get_related_info(self, data, ids):
        from users.models import Profile
        followers_ids = set(f_id for id in ids for f_id in data[id]['followers']['ids'])
        f_info = Profile.objects.info_for(followers_ids, related=False)

        for id in ids:
            data[id]['followers']['entities'] = [f_info[f_id] for f_id in data[id]['followers']['ids']
                    if f_id in f_info]

    def followed(self, ids, entity_model):
        """ Return entities followed by users {id: {'count': count, 'ids': [top_followed_ids]}} """
        followed_data = list(self.filter(content_type=ContentType.objects.get_for_model(entity_model),
                follower__id__in=ids).values_list('entity_id', 'follower'))

        followed_points = entity_model.objects.filter(id__in=map(lambda f: f[0], followed_data)) \
                .values_list('id', 'points')

        res = {}
        for id in ids:
            e_ids = map(lambda fd: fd[0], filter(lambda f: f[1]==id, followed_data))
            top_followed_points = sorted(filter(lambda f: f[0] in e_ids, followed_points),
                    key=lambda f: f[1], reverse=True)[:settings.TOP_FOLLOWED_COUNT]
            res[id] = {
                'count': len(e_ids),
                'ids': map(lambda f: f[0], top_followed_points),
            }
        return res

    def is_followed(self, entity, profile):
        if 'followers' not in type(entity).features:
            return False

        return self.filter(content_type=ContentType.objects.get_for_model(entity),
                entity_id=entity.id, follower=profile).exists()

    def add(self, entity, profile):
        # TODO: user should not follow himself
        if 'followers' not in type(entity).features:
            return

        self.get_or_create(content_type=ContentType.objects.get_for_model(entity),
                entity_id=entity.id, follower=profile)
        profile.clear_cache()
        entity.clear_cache()

    def remove(self, entity, profile):
        if 'followers' not in type(entity).features:
            return

        self.filter(content_type=ContentType.objects.get_for_model(entity),
                entity_id=entity.id, follower=profile).delete()
        profile.clear_cache()
        entity.clear_cache()

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

        # TODO: move it out of here (?)
        features_models = {'resources': EntityResource, 'followers': EntityFollower,
                'locations': EntityLocation}

        cached_ids = []
        res = {}
        for key, entity in cached_entities.iteritems():
            id = int(key[len(cache_prefix):])
            cached_ids.append(id)
            res[id] = entity

        other_ids = set(ids) - set(cached_ids)
        if len(other_ids) > 0:
            # TODO: what if some ids are not available anymore (here or in one of get_for)?
            #       (drop id if data for at least one feature is missing? - here and in get_info())
            content_type_id = ContentType.objects.get_for_model(self.model).id
            other_res = dict((id, {'ct': content_type_id}) for id in other_ids)

            for feature in features:
                feature_data = features_models[feature].objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id][feature] = feature_data[id]

            # Add custom model info
            self.get_info(other_res)

            cache_res = dict((cache_prefix+str(id), other_res[id]) for id in other_res)
            cache.set_many(cache_res, 60) # TODO: specify time as a model attribute

            res.update(other_res)

        if related:
            for feature in features:
                features_models[feature].objects.get_related_info(res, ids)

            self.get_related_info(res, ids)

        return res

    def get_info(self, data):
        """ Take {id: info} filled with features data and add the rest information """
        raise NotImplemented

    def get_related_info(self, data, ids):
        """ Take {id: info} and add info from related features """
        pass

    # TODO: cache count separately?
    # TODO: take is_main into account
    # TODO: cache it (at least for data for side panels) - in Location
    def for_location(self, location, start=0, limit=None, sort_by=('-points',)):
        """ Return {'ids': sorted_entities_ids, 'count': total_count} """
        res = {}
        if location.is_country():
            # Special processing to minify entity_query
            entity_query = Q()
            res['count'] = self.count()
        else:
            loc_query = Q(location__id=location.id)

            field = location.children_query_field()
            if field:
                loc_query |= Q(**{'location__'+field: location.id})

            entity_ids = set(EntityLocation.objects.filter(
                    content_type=ContentType.objects.get_for_model(self.model)) \
                    .filter(loc_query).values_list('entity_id', flat=True))

            # TODO: what happens when the list of ids is too long (for the next query)?
            entity_query = Q(id__in=entity_ids)

            res['count'] = len(entity_ids)

        ids = self.filter(entity_query).order_by(*sort_by).values_list('id', flat=True)
        res['ids'] = ids[slice(start, start+limit if limit else None)]

        return res

# TODO: add admins, complaints, files/images
# TODO: reset cache key on changing any of related data or save/delete (base method/decorator)
class BaseEntityModel(models.Model):
    points = models.IntegerField(u'Очки', default=0) # used for sorting entities

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)
    add_time = models.DateTimeField(auto_now_add=True, null=True, db_index=True)

    objects = BaseEntityManager()

    cache_prefix = ''
    features = [] # 'resources', 'followers', 'locations',  # TODO: 'complaints', 'admins'

    class Meta:
        abstract = True

    def cache_key(self):
        return self.cache_prefix + str(self.id)

    def clear_cache(self):
        cache.delete(self.cache_key())

    def info(self, related=True):
        # TODO: this code can fail
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
