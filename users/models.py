# -*- coding:utf-8 -*-
import inspect

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.participants.models import EntityParticipant
from elements.models import BaseEntityManager, BaseEntityModel, ENTITIES_MODELS, \
        entity_class, HTMLField
from elements.resources.models import EntityResource

class ProfileManager(BaseEntityManager):
    def get_info(self, data, ids):
        # TODO: add info on non-profile entities followed by the user

        # Get contacts
        contacts = EntityParticipant.objects.participant_in('follower', ids, Profile)
        for id in ids:
            data[id]['contacts'] = contacts[id]

        participants_data = list(EntityParticipant.objects.filter(person__in=ids).values_list('content_type', 'entity_id', 'role', 'person'))

        # TODO: use ratings to sort entities

        for entity_name in ('ideas', 'tasks', 'projects'):
            model = ENTITIES_MODELS[entity_name]

            for id in ids:
                data[id][entity_name] = dict((role, {'ids': []}) for role in model.roles)

            model_ct_id = ContentType.objects.get_for_model(model).id
            for ct_id, e_id, role, id in filter(lambda p: p[0]==model_ct_id, participants_data):
                data[id][entity_name][role]['ids'].append(e_id)

            for id in ids:
                for role in model.roles:
                    data[id][entity_name][role]['count'] = len(data[id][entity_name][role]['ids'])

    def get_related_info(self, data, ids):
        contacts_ids = set(c_id for id in ids for c_id in data[id]['contacts']['ids'])
        contacts_info = Profile.objects.info_for(contacts_ids, related=False)
        for id in ids:
            data[id]['contacts']['entities'] = [contacts_info[c_id] for c_id in data[id]['contacts']['ids']
                            if c_id in contacts_info]

        for entity_name in ('ideas', 'tasks', 'projects'):
            model = ENTITIES_MODELS[entity_name]

            entities_ids = set(e_id for id in ids for role in model.roles \
                    for e_id in data[id][entity_name][role]['ids'])
            entities_info = model.objects.info_for(entities_ids, related=False)

            for id in ids:
                for role in model.roles:
                    data[id][entity_name][role]['entities'] = [entities_info[e_id] \
                            for e_id in data[id][entity_name][role]['ids']]

@entity_class(['resources', 'locations', 'participants'])
class Profile(BaseEntityModel):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30, db_index=True)

    first_name = models.CharField(u'Имя', max_length=40, help_text=u'на русском языке')
    last_name = models.CharField(u'Фамилия', max_length=40, help_text=u'на русском языке')
    show_name = models.BooleanField(u'Показывать настоящее имя', default=True,
            help_text=u'Снимите эту галку, чтобы скрыть свое имя от других пользователей')

    intro = models.CharField(u'Кратко о себе', max_length=100, blank=True,
            help_text=u'например: "юрист", "создатель проекта Гракон", "любитель рисовать карикатуры"')
    about = HTMLField(u'О себе', default='', blank=True)

    objects = ProfileManager()

    entity_name = 'participants'
    entity_title = u'Участники'
    cache_prefix = 'user_info/'
    editable_fields = ['first_name', 'last_name', 'intro', 'about']

    table_header = 'profiles/table_header.html'
    table_line = 'profiles/table_line.html'

    roles = ['follower']

    follow_button = {
        'role': 'follower',
        'cancel_msg': u'Вы хотите удалить этого пользователя из списка контактов?',
        'cancel_btn': u'Удалить',
        'cancel_btn_long': u'Удалить из контактов',
        'confirm_msg': u'Вы хотите добавить этого пользователя в список контактов?',
        'confirm_btn': u'Добавить',
        'confirm_btn_long': u'Добавить в контакты',
    }

    def calc_rating(self):
        info = self.info()
        return info['tasks']['admin']['count'] + info['ideas']['admin']['count'] + 3*info['projects']['admin']['count']

    def has_contact(self, profile):
        return EntityParticipant.objects.is_participant(profile, self, 'follower')

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.username])

    def __unicode__(self):
        return self.first_name + u' ' + self.last_name

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)

class Message(models.Model):
    sender = models.ForeignKey(Profile, verbose_name=u'Отправитель', related_name='sent_messages')
    receiver = models.ForeignKey(Profile, verbose_name=u'Получатель', related_name='received_messages')
    title = models.CharField(u'Тема', max_length=100)
    body = models.TextField(u'Сообщение')
    show_email = models.BooleanField(u'Показать email получателю', default=True)
    time = models.DateTimeField(auto_now=True)
