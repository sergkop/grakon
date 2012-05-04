# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField

class OfficialManager(BaseEntityManager):
    def get_info(self, data, ids):
        officials_by_id = self.in_bulk(ids)
        for id in ids:
            data[id]['official'] = officials_by_id[id]

# TODO: url - for official website/page (maybe several) (element for that?)
# TODO: introduce type
@entity_class(['followers', 'locations', 'admins'])
class Official(BaseEntityModel):
    first_name = models.CharField(u'Имя', max_length=50)
    middle_name = models.CharField(u'Отчество', max_length=50, blank=True)
    last_name = models.CharField(u'Фамилия', max_length=70)

    address = models.CharField(u'Адрес', max_length=250, blank=True)
    telephone = models.CharField(u'Телефон', max_length=100, blank=True)
    email = models.EmailField(u'Электронная почта', blank=True)
    about = HTMLField(u'О чиновнике', blank=True)

    objects = OfficialManager()

    cache_prefix = 'official/'
    table_header = 'tables/officials_header.html'
    table_line = 'tables/officials_line.html'

    @models.permalink
    def get_absolute_url(self):
        return ('official', [self.id])

    def __unicode__(self):
        return u'%s %s %s' % (self.last_name, self.first_name, self.middle_name)
