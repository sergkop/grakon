# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.db.models import Q

from elements.models import ENTITIES_MODELS
from services.cache import cache_function

class LocationManager(models.Manager):
    @cache_function('location/country', 1000)
    def country(self):
        return self.get(country=None)

    def info_for(self, ids, related=True):
        """
        Return {id: {'location': location, entities_keys: entities_data}}.
        If related is True, return list of entities data, otherwise - only ids.
        """
        cache_prefix = self.model.cache_prefix
        cached_locations = cache.get_many([cache_prefix+str(id) for id in ids])

        cached_ids = []
        res = {}
        for key, entity in cached_locations.iteritems():
            id = int(key[len(cache_prefix):])
            cached_ids.append(id)
            res[id] = entity

        other_ids = set(ids) - set(cached_ids)
        if len(other_ids) > 0:
            other_res = dict((id, {}) for id in other_ids)

            locations = self.filter(id__in=other_ids).select_related()
            for loc in locations:
                other_res[loc.id] = {'location': loc}

                # TODO: separate participants and tools
                for name, model in ENTITIES_MODELS.iteritems():
                    if name == 'posts': # TODO: hack
                        continue
                    count_name = 'participants' if name=='participants' else 'tools'
                    other_res[loc.id][name] = loc.get_entities(name)(
                            limit=settings.LIST_COUNT[count_name])

            res.update(other_res)

            cache_res = dict((cache_prefix+str(id), other_res[id]) for id in other_res)
            cache.set_many(cache_res, 60) # TODO: specify time outside of this method

        if related:
            for name, model in ENTITIES_MODELS.iteritems():
                if name == 'posts':
                    continue
                e_ids = set(e_id for id in ids for e_id in res[id][name]['ids'])
                e_info = model.objects.info_for(e_ids, related=False)

                for id in ids:
                    res[id][name]['entities'] = [e_info[e_id] for e_id in res[id][name]['ids']
                            if e_id in e_info]

        return res

# TODO: add wiki_url
# TODO: determine type of location (part of a city, city, district, etc. and use for autocompletion title)
class Location(models.Model):
    country = models.ForeignKey('self', null=True, blank=True, related_name='country_related')
    region = models.ForeignKey('self', null=True, blank=True, related_name='region_related')
    district = models.ForeignKey('self', null=True, blank=True, related_name='district_related')

    okato_id = models.CharField(u'Идентификатор ОКАТО', max_length=11, db_index=True)

    name = models.CharField(max_length=150, db_index=True)

    objects = LocationManager()

    cache_prefix = 'location_info'

    def level(self):
        if self.country_id is None:
            return 1
        elif self.region_id is None:
            return 2
        elif self.district_id is None:
            return 3
        else:
            return 4

    def is_country(self):
        return self.country_id is None

    def is_region(self):
        return self.country_id is not None and self.region_id is None

    def is_district(self):
        return self.region_id is not None and self.district_id is None

    def is_location(self):
        return self.district_id is not None

    # TODO: cache it (use internal self attribute)
    def is_lowest_level(self):
        if not self.region:
            return False

        if self.is_district():
            return not Location.objects.filter(district=self).exists()
        else:
            return True

    def children_query_field(self):
        """ Return name of of Location field to construct db query filtering children """
        i = self.level() - 1
        return ['country', 'region', 'district'][i] if i<3 else None

    def info(self, related=True):
        return Location.objects.info_for([self.id], related)[self.id]

    def cache_key(self):
        return self.cache_prefix + str(self.id)

    def clear_cache(self):
        cache.delete(self.cache_key())

    # TODO: cache count separately?
    # TODO: take is_main into account
    # TODO: cache it (at least for data for side panels) - in Location
    def get_entities(self, entity_type):
        """ Return {'ids': sorted_entities_ids, 'count': total_count} """
        from elements.locations.models import EntityLocation
        model = ENTITIES_MODELS[entity_type]

        def method(start=0, limit=None, sort_by=('-rating',)):
            entity_query = Q()

            # Filter out unactivated accounts
            # TODO: make queryset a parameter of entity model (?)
            if model.entity_name == 'participants':
                entity_query = Q(user__is_active=True)

            if not self.is_country(): # used to speed up processing
                loc_query = Q(location__id=self.id)

                field = self.children_query_field()
                if field:
                    loc_query |= Q(**{'location__'+field: self.id})

                entity_ids = set(EntityLocation.objects.filter(
                        content_type=ContentType.objects.get_for_model(model)) \
                        .filter(loc_query).values_list('entity_id', flat=True))

                # TODO: what happens when the list of ids is too long (for the next query)? - use subqueries
                entity_query &= Q(id__in=entity_ids)

            ids = model.objects.filter(entity_query).order_by(*sort_by).values_list('id', flat=True)
            return {
                'count': ids.count(),
                'ids': ids[slice(start, start+limit if limit else None)],
            }

        return method

    def __unicode__(self, full_path=False):
        name = self.name

        if full_path:
            if self.district_id:
                name = unicode(self.district) + u'->' + name
            if self.region_id:
                name = unicode(self.region) + u'->' + name
        return name

    @models.permalink
    def get_absolute_url(self):
        return ('location_wall', (), {'loc_id': str(self.id)})
