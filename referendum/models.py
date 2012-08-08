# -*- coding:utf-8 -*-
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class
from locations.models import Location

class QuestionManager(BaseEntityManager):
    pass

@entity_class(['participants', 'comments'])
class Question(BaseEntityModel):
    title = models.CharField(max_length=250)

    objects = QuestionManager()

    entity_name = 'questions'
    entity_title = u'Вопросы'
    cache_prefix = 'questions/'

    roles = ['follower']

    follow_button = {
        'role': 'follower',
        'cancel_msg': u'Вы хотите отказаться от поддержки вынесения вопроса на референдум?',
        'cancel_btn': u'Отказаться',
        'cancel_btn_long': u'Отказаться',
        'confirm_msg': u'Поддержать вынесение вопроса на референдум?',
        'confirm_btn': u'Поддержать',
        'confirm_btn_long': u'Поддержать',
    }

    def calc_rating(self):
        return self.info()['participants']['follower']['count']

    @models.permalink
    def get_absolute_url(self):
        return ('question', [self.id])

    def __unicode__(self):
        return self.title


class InitiativeGroupManager(BaseEntityManager):
    def get_info(self, data, ids):
        locations_by_id = Location.objects.in_bulk(data[id]['instance']['location_id'] for id in ids)
        for id in ids:
            data[id]['location'] = locations_by_id[data[id]['instance']['location_id']]

@entity_class(['participants', 'comments'])
class InitiativeGroup(BaseEntityModel):
    location = models.ForeignKey(Location)

    objects = InitiativeGroupManager()

    entity_name = 'initiative_groups'
    entity_title = u'Инициативные группы'
    cache_prefix = 'initiative_group/'

    roles = ['follower']

    follow_button = {
        'role': 'follower',
        'cancel_msg': u'Вы хотите выйти из инициативной группы?',
        'cancel_btn': u'Выйти',
        'cancel_btn_long': u'Выйти из группы',
        'confirm_msg': u'Вы хотите вступить в инициативную группу?',
        'confirm_btn': u'Вступить',
        'confirm_btn_long': u'Вступить в группу',
    }

    def calc_rating(self):
        return self.info()['participants']['follower']['count']

    @models.permalink
    def get_absolute_url(self):
        return ('initiative_group', [self.id])

    def __unicode__(self):
        return self.location.name
