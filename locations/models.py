# -*- coding:utf-8 -*-
from django.db import models

from services.cache import cache_function

class LocationManager(models.Manager):
    @cache_function('location/country', 1000)
    def country(self):
        return self.get(country=None)

# TODO: method for caching related data (like in profile)
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
