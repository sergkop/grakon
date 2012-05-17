# -*- coding:utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField
from posts.models import EntityPost

class OfficialManager(BaseEntityManager):
    def get_info(self, data, ids):
        opinions_data = EntityPost.objects.filter(content_type=ContentType.objects.get_for_model(Official),
                entity_id__in=ids).exclude(opinion='neutral').values_list('entity_id', 'opinion')

        for id in ids:
            opinions = map(lambda op: op[1], filter(lambda op: op[0]==id, opinions_data))
            data[id]['posts']['positive'] = opinions.count('positive')
            data[id]['posts']['negative'] = opinions.count('negative')

# TODO: url - for official website/page (maybe several) (element for that?)
# TODO: introduce choices for types
@entity_class(['locations', 'participants', 'posts'])
class Official(BaseEntityModel):
    first_name = models.CharField(u'Имя', max_length=50)
    middle_name = models.CharField(u'Отчество', max_length=50, blank=True)
    last_name = models.CharField(u'Фамилия', max_length=70)

    post = models.CharField(u'Должность', max_length=100)
    place = models.CharField(u'Место работы', max_length=150, help_text=u'Например, Московский городской суд')
    address = models.CharField(u'Рабочий адрес', max_length=250, blank=True)
    telephone = models.CharField(u'Телефон', max_length=100, blank=True)
    email = models.EmailField(u'Электронная почта', blank=True)
    about = HTMLField(u'О чиновнике', blank=True)

    objects = OfficialManager()

    entity_name = 'officials'
    entity_title = u'Чиновники'
    cache_prefix = 'official/'
    table_header = 'officials/table_header.html'
    table_line = 'officials/table_line.html'
    table_cap = 'officials/table_cap.html'

    roles = ['admin', 'follower']

    @models.permalink
    def get_absolute_url(self):
        return ('official', [self.id])

    def __unicode__(self):
        return u'%s %s %s' % (self.last_name, self.first_name, self.middle_name)
