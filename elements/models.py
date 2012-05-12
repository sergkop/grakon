# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models

from tinymce.models import HTMLField as TinyMCEHTMLField

from elements.utils import reset_cache
from locations.models import Location

class BaseEntityPropertyManager(models.Manager):
    def get_for(self, model, ids):
        raise NotImplemented()

    # TODO: rename it not to overlap with BaseEntityModel method
    def get_related_info(self, data, ids):
        if not self.model.fk_field:
            return

        feature = self.model.feature
        related_ids = set(r_id for id in ids for r_id in data[id][feature]['ids'])
        related_model = self.model._meta.get_field(self.model.fk_field).rel.to
        r_info = related_model.objects.info_for(related_ids, related=False)

        for id in ids:
            data[id][feature]['entities'] = [r_info[r_id] for r_id in data[id][feature]['ids']
                    if r_id in r_info]

    def _add_remove(self, entity, instance, add, params={}):
        """ Instance corresponds to the only non-content_type foreign key of the model """
        if not self.model.fk_field:
            raise ValueError(self.model._meta.object_name+" model doesn't allow add() method")

        if self.model.feature not in type(entity).features:
            return

        if add:
            self.get_or_create(content_type=ContentType.objects.get_for_model(type(entity)),
                    entity_id=entity.id, defaults=params, **{self.model.fk_field: instance})
        else:
            # Use generic relation to filter related feature instances
            getattr(entity, self.model.feature).filter(**{self.model.fk_field: instance}).delete()

        if self.model.points_sources:
            from users.models import Profile
            profiles = [x for x in [entity, instance] if type(x) is Profile]
            for profile in profiles:
                for source in self.model.points_sources:
                    profile.update_source_points(source)

        entity.clear_cache()
        instance.clear_cache()

    def add(self, entity, instance, params={}):
        self._add_remove(entity, instance, True, params)

    def remove(self, entity, instance):
        self._add_remove(entity, instance, False)

FEATURES_MODELS = {}

class BaseEntityProperty(models.Model):
    content_type = models.ForeignKey(ContentType)
    entity_id = models.PositiveIntegerField(db_index=True)
    entity = generic.GenericForeignKey('content_type', 'entity_id')

    time = models.DateTimeField(auto_now=True, db_index=True)

    feature = None # name of corresponding feature
    fk_field = None # specify if there is another foreign key field besides content_type
    points_sources = []

    objects = BaseEntityPropertyManager()

    class Meta:
        abstract = True

    """
    def save(self):
        super(BaseEntityProperty, self).save()

        if type(self).points_sources:
            profiles = []

            from users.models import Profile
            if self.content_type.get_model() == Profile:
                profiles.append(Profile(id))

            if self.fk_field:
                related_model = type(self)._meta.get_field(self.model.fk_field).rel.to

            profiles = [x for x in instances if type(x) is Profile]
            for profile in profiles:
                for source in self.model.points_sources:
                    profile.update_source_points(source)
    """

def feature_model(cls):
    FEATURES_MODELS[cls.feature] = cls
    return cls

# TODO: add subcategories (?)
# (name, title)
RESOURCE_CHOICES = (
    ('money', u'спонсор/деньги'),
    ('time', u'волонтер/время'),
    ('transport', u'автомобиль/автобус'),
    ('printing', u'типография/печать'),
    ('premises', u'помещение/заведение'),
    ('food', u'повар/общественное питание'),

    ('authority', u'представитель власти'),
    ('organization', u'представитель большой организации'),

    ('lawyer', u'юрист/адвокат/правозащитник'),
    ('journalist', u'журналист/представитель СМИ'),
    ('observer', u'опыт наблюдения на выборах'),
    ('design', u'дизайнер/художник/оформитель'),
    ('programmer', u'программист/веб-разработчик'),
    ('copywriting', u'копирайтер/писатель/поэт'),
    ('photographer', u'фотограф/оператор/монтажер'),
    ('organizator', u'организатор мероприятий'),
    ('computer', u'продвинутый пользователь компьютера'),
    ('pr', u'PR специалист/специалист по продвижению'),
    ('creative', u'креативщик/генератор идей/нэймер'),
    ('musician', u'музыкант/певец/диджей'),
    ('narrator', u'оратор/ведущий/диктор'),
    ('actor', u'актер/шоумэн'),
    ('interpreter', u'переводчик'),
    ('strong', u'физическая сила'),
    ('auditory', u'большое количество друзей'),

    #('people', u'Человеческие ресурсы'), #u'Возможность предоставить волонтеров или наемных рабочих со скидкой'),
    # учитель/преподаватель
    #('other', u'Другое', u''),
)

RESOURCE_DICT = dict((name, title) for name, title in RESOURCE_CHOICES)

class EntityResourceManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return {id: [resources]} """
        res = dict((id, []) for id in ids)
        for id, resource in self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'resource'):
            res[id].append({'name': resource, 'title': RESOURCE_DICT[resource]})
        return res

    def update(self, entity, resources):
        if self.model.feature not in type(entity).features:
            return

        # Filter out resources not from the list
        resources = set(RESOURCE_DICT.keys()) & set(resources)

        entity_resources = list(getattr(entity, self.model.feature).all())
        new_resources = resources - set(er.resource for er in entity_resources)

        for er in entity_resources:
            if er.resource not in resources:
                er.delete()

        # TODO: this can cause IntegrityError
        self.bulk_create([self.model(entity=entity, resource=resource) for resource in new_resources])

        from users.models import Profile
        if type(entity) is Profile:
            entity.update_source_points('resources')

        entity.clear_cache()

# TODO: ability to add text, describing resources + custom resources (in case of other)
@feature_model
class EntityResource(BaseEntityProperty):
    resource = models.CharField(u'Ресурс', max_length=20, choices=RESOURCE_CHOICES, db_index=True)

    objects = EntityResourceManager()

    feature = 'resources'
    points_sources = ['resources']

    class Meta:
        unique_together = ('content_type', 'entity_id', 'resource')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.resource)

class EntityLocationManager(BaseEntityPropertyManager):
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
        super(EntityLocationManager, self).get_related_info(data, ids)

        for id in ids:
            id_data = data[id][self.model.feature]
            id_data['main'] = (filter(lambda d: d['location'].id==id_data['main_id'],
                    id_data['entities']) or [None])[0]

# TODO: some models may need only one location (?)
# TODO: reset cache on save()/delete() (here and in other models)
@feature_model
class EntityLocation(BaseEntityProperty):
    location = models.ForeignKey(Location, related_name='entities')
    is_main = models.BooleanField(default=False, db_index=True)

    objects = EntityLocationManager()

    feature = 'locations'
    fk_field = 'location'

    class Meta:
        unique_together = ('content_type', 'entity_id', 'location')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.location)

# TODO: avoid importing profile in many places
# TODO: user should not follow himself
class EntityFollowerManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return followers data {id: {'count': count, 'ids': [top_followers_ids]}} """
        followers_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'follower'))

        from users.models import Profile
        followers_rating = Profile.objects.filter(id__in=map(lambda f: f[1], followers_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            f_ids = map(lambda fd: fd[1], filter(lambda f: f[0]==id, followers_data))
            top_followers_rating = sorted(filter(lambda f: f[0] in f_ids, followers_rating),
                    key=lambda f: f[1], reverse=True)[:settings.LIST_COUNT['followers']]
            res[id] = {
                'count': len(f_ids),
                'ids': map(lambda f: f[0], top_followers_rating),
            }
        return res

    def followed(self, ids, entity_model):
        """ Return entities followed by users {id: {'count': count, 'ids': [top_followed_ids]}} """
        followed_data = list(self.filter(content_type=ContentType.objects.get_for_model(entity_model),
                follower__id__in=ids).values_list('entity_id', 'follower'))

        followed_rating = entity_model.objects.filter(id__in=map(lambda f: f[0], followed_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            e_ids = map(lambda fd: fd[0], filter(lambda f: f[1]==id, followed_data))
            top_followed_rating = sorted(filter(lambda f: f[0] in e_ids, followed_rating),
                    key=lambda f: f[1], reverse=True)[:settings.LIST_COUNT['followed']]
            res[id] = {
                'count': len(e_ids),
                'ids': map(lambda f: f[0], top_followed_rating),
            }
        return res

    def is_followed(self, entity, profile):
        if self.model.feature not in type(entity).features:
            return False
        return getattr(entity, self.model.feature).filter(follower=profile).exists()

@feature_model
class EntityFollower(BaseEntityProperty):
    follower = models.ForeignKey('users.Profile', related_name='followed_entities')

    objects = EntityFollowerManager()

    feature = 'followers'
    fk_field = 'follower'
    points_sources = ['contacts', 'follows']

    class Meta:
        unique_together = ('content_type', 'entity_id', 'follower')

    def __unicode__(self):
        return unicode(self.follower) + ' follows ' + unicode(self.entity)

# TODO: similar to follower model code
class EntityAdminManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return admins data {id: {'count': count, 'ids': [ids]}} """
        admins_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'admin'))

        from users.models import Profile
        admins_rating = Profile.objects.filter(id__in=map(lambda a: a[1], admins_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            a_ids = map(lambda ad: ad[1], filter(lambda a: a[0]==id, admins_data))
            top_admin_rating = sorted(filter(lambda a: a[0] in a_ids, admins_rating),
                    key=lambda a: a[1], reverse=True)[:settings.LIST_COUNT['admins']]
            res[id] = {
                'count': len(a_ids),
                'ids': map(lambda a: a[0], top_admin_rating),
            }
        return res

    def is_admin(self, entity, profile):
        if self.model.feature not in type(entity).features:
            return False
        return getattr(entity, self.model.feature).filter(admin=profile).exists()

    # TODO: take params for pagination
    def administered_by(self, profile):
        """ Return {'count': count, 'entities': [top_entities_info]} """
        entities_data = list(profile.administered_entities.values_list('content_type', 'entity_id'))

        entities_by_ct = {}
        for ct_id, e_id in entities_data:
            entities_by_ct.setdefault(ct_id, []).append(e_id)

        entities = []
        for ct_id in entities_by_ct:
            model = ContentType.objects.get_for_id(ct_id).model_class()
            entities += model.objects.info_for(entities_by_ct[ct_id], related=False).values()

        return {'count': len(entities_data),
                'entities': sorted(entities, key=lambda e: -e['instance'].rating)[:settings.LIST_COUNT['admins']]}

@feature_model
class EntityAdmin(BaseEntityProperty):
    admin = models.ForeignKey('users.Profile', related_name='administered_entities')

    objects = EntityAdminManager()

    feature = 'admins'
    fk_field  = 'admin'
    points_sources = ['admin']

    class Meta:
        unique_together = ('content_type', 'entity_id', 'admin')

    def __unicode__(self):
        return unicode(self.admin) + ' is admin of ' + unicode(self.entity)

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
            # TODO: what if some ids are not available anymore (here or in one of get_for)?
            #       (drop id if data for at least one feature is missing? - here and in get_info())
            content_type_id = ContentType.objects.get_for_model(self.model).id
            other_res = dict((id, {'ct': content_type_id}) for id in other_ids)

            # Get entity instances
            entities_by_id = self.in_bulk(other_ids)
            for id in other_ids:
                other_res[id]['instance'] = entities_by_id[id]

            for feature in features:
                feature_data = FEATURES_MODELS[feature].objects.get_for(self.model, other_ids)
                for id in other_ids:
                    other_res[id][feature] = feature_data[id]

            # Add custom model info
            self.get_info(other_res, other_ids)

            cache_res = dict((cache_prefix+str(id), other_res[id]) for id in other_res)
            cache.set_many(cache_res, 60) # TODO: specify time as a model attribute

            res.update(other_res)

        if related:
            for feature in features:
                FEATURES_MODELS[feature].objects.get_related_info(res, ids)

            self.get_related_info(res, ids)

        return res

    def get_info(self, data, ids):
        """ Take {id: info} filled with features data and add the rest information """
        pass

    def get_related_info(self, data, ids):
        """ Take {id: info} and add info from related features """
        pass

# TODO: add complaints, files/images
# TODO: reset cache key on changing any of related data or save/delete (base method/decorator)
class BaseEntityModel(models.Model):
    rating = models.IntegerField(default=0, editable=False) # used for sorting entities

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)
    add_time = models.DateTimeField(auto_now_add=True, null=True, db_index=True)

    objects = BaseEntityManager()

    entity_name = ''
    cache_prefix = ''
    features = [] # 'resources', 'followers', 'locations', 'complaints', 'admins'

    # Paths to templates constructing tables
    table_header = ''
    table_line = ''
    table_cap = '' # Used on locations pages

    class Meta:
        abstract = True

    def cache_key(self):
        return self.cache_prefix + str(self.id)

    def clear_cache(self):
        cache.delete(self.cache_key())

    def info(self, related=True):
        # TODO: this code can fail
        return type(self).objects.info_for([self.id], related)[self.id]

    # TODO: recalculate rating on save or in celery (?) and reset cache
    def calc_rating(self):
        """ Return rating using entity info """
        raise NotImplemented

    @reset_cache
    def save(self, *args, **kwargs):
        return super(BaseEntityModel, self).save(*args, **kwargs)

    @reset_cache
    def delete(self, *args, **kwargs):
        return super(BaseEntityModel, self).delete(*args, **kwargs)

    # TODO: move it inside feature class
    def get_admins(self, start=0, limit=None, sort_by=('-admin__rating',)):
        if 'admins' not in type(self).features:
            return None

        queryset = self.admins.order_by(*sort_by)
        return {
            'count': queryset.count(),
            'ids': queryset.values_list('admin', flat=True)[slice(start, start+limit if limit else None)],
        }

    # TODO: generate sort_by appending feature_model.feature+'__'
    def get_followers(self, start=0, limit=None, sort_by=('-follower__rating',)):
        if 'followers' not in type(self).features:
            return None

        feature_model = FEATURES_MODELS['followers']
        queryset = getattr(self, feature_model.feature).order_by(*sort_by)
        return {
            'count': queryset.count(),
            'ids': queryset.values_list(feature_model.fk_field, flat=True) \
                    [slice(start, start+limit if limit else None)],
        }

    def get_posts(self, start=0, limit=None, sort_by=('-rating',)):
        if 'posts' not in type(self).features:
            return None

        feature_model = FEATURES_MODELS['posts']
        queryset = getattr(self, feature_model.feature).order_by(*sort_by)
        return {
            'count': queryset.count(),
            'ids': queryset.values_list('id', flat=True) \
                    [slice(start, start+limit if limit else None)],
        }

ENTITIES_MODELS = {}

@reset_cache
def update_resources(self, resources):
    EntityResource.objects.update(self, resources)

def entity_class(features):
    """ Return decorator for entity model """
    def decorator(cls):
        new_cls = type(cls.__name__, (cls,), {'__module__': cls.__module__})
        new_cls.features = features
        ENTITIES_MODELS[new_cls.entity_name] = new_cls

        if 'resources' in features:
            new_cls.update_resources = update_resources

        # Create generic relations
        for feature in FEATURES_MODELS:
            field = generic.GenericRelation(FEATURES_MODELS[feature], object_id_field='entity_id')
            field.contribute_to_class(new_cls, feature)

        return new_cls

    return decorator

class HTMLField(TinyMCEHTMLField):
    def formfield(self, **kwargs):
        from elements.forms import HTMLCharField
        kwargs['form_class'] = HTMLCharField
        return super(HTMLField, self).formfield(**kwargs)

    def south_field_triple(self):
        """ Hack to deal with south migrations """
        field_class = self.__class__.__module__ + '.' + self.__class__.__name__
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
