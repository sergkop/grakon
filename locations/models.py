# -*- coding:utf-8 -*-
from django.db import models

# TODO: method for caching related data (like in profile)
# TODO: add wiki_url
class Location(models.Model):
    country = models.ForeignKey('self', null=True, blank=True, related_name='country_related')
    region = models.ForeignKey('self', null=True, blank=True, related_name='region_related')
    district = models.ForeignKey('self', null=True, blank=True, related_name='district_related')

    okato_id = models.CharField(u'Идентификатор ОКАТО', max_length=11, db_index=True)

    name = models.CharField(max_length=150, db_index=True)

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
