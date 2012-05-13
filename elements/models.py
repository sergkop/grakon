# -*- coding:utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models

from tinymce.models import HTMLField as TinyMCEHTMLField

from elements.utils import reset_cache

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
    entity_title = ''
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
    from elements.resources.models import EntityResource # TODO: move it out of here
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
