# -*- coding:utf-8 -*-
from django.core.cache import cache
from django.db import models

from services.cache import cache_function

class LocationManager(models.Manager):
    @cache_function('location/country', 1000)
    def country(self):
        return self.get(country=None)

    # TODO: this method is similar to BaseEntityManager.info_for
    def info_for(self, ids, related=True):
        """
        Return {id: {'location': location, entities_keys: entities_data}}.
        If related is True, return list of entities data, otherwise - only ids.
        """
        cache_prefix = 'location_info'
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

            from users.models import Profile
            entities_models = {'participants': Profile} # TODO: make it global dict?

            locations = list(self.filter(id__in=ids).select_related())
            for location in locations:
                other_res[location.id] = {
                    'location': location,
                    #'name': location.name,
                    #'path': location.path(),
                }

                for name, model in entities_models.iteritems():
                    # TODO: limit should be taken from settings per entity model
                    entities_ids = model.objects.for_location(location, limit=3)
                    if related:
                        entities_data = model.objects.info_for(entities_ids, related=False)
                        other_res[location.id][name] = [entities_data[id] for id in entities_ids]
                    else:
                        other_res[location.id][name] = entities_ids

            # TODO: the cached values should contain only list of entities ids
            cache_res = {}
            for id, info in other_res.iteritems():
                cache_res[cache_prefix+str(id)] = info

            cache.set_many(cache_res, 60) # TODO: specify time outside of this method

            res.update(other_res)

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

    def children_query_field(self):
        """ Return name of of Location field to construct db query filtering children """
        i = self.level() - 1
        return ['country', 'region', 'district'][i] if i<3 else None

    def info(self, related=True):
        return Location.objects.info_for([self.id], related)[self.id]

    #def path(self):
    #    """ Return [(id, name)]. It uses instances of parent locations. """
    #    res = []
    #    if self.region_id:
    #        res.append((self.region_id, self.region.name))
    #    if self.district_id:
    #        res.append((self.district_id, self.district.name))
    #    res.append((self.id, self.name))
    #    return res

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
        return ('location', (), {'loc_id': str(self.id)})
