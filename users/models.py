# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from tinymce.models import HTMLField

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, EntityFollower

class ProfileManager(BaseEntityManager):
    def get_info(self, data):
        ids = data.keys()

        profiles_by_id = dict((p.id, p) for p in self.filter(id__in=ids))
        for id in ids:
            if id in profiles_by_id:
                data[id]['profile'] = profiles_by_id[id]
            else:
                del data[id] # TODO: do we need it?

        # TODO: add info on non-profile entities followed by the user

        contacts = EntityFollower.objects.followed(ids, Profile)
        for id in ids:
            data[id]['contacts'] = contacts[id]

    def get_related_info(self, data, ids):
        contacts_ids = set(c_id for id in ids for c_id in data[id]['contacts']['ids'])
        contacts_info = Profile.objects.info_for(contacts_ids, related=False)
        for id in ids:
            data[id]['contacts']['entities'] = [contacts_info[c_id] for c_id in data[id]['contacts']['ids']
                            if c_id in contacts_info]

class Profile(BaseEntityModel):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)

    first_name = models.CharField(u'Имя', max_length=40)
    last_name = models.CharField(u'Фамилия', max_length=40)
    show_name = models.BooleanField(u'Показывать настоящее имя', default=False,
            help_text=u'<b>Поставьте эту галку, чтобы другие пользователи видели ваше настоящее имя</b>')

    about = HTMLField(u'О себе', default='', blank=True)

    objects = ProfileManager()

    cache_prefix = 'user_info/'

    def calc_points(self):
        pass # TODO: implement it

    def has_contact(self, profile):
        return EntityFollower.objects.is_followed(profile, self)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.username])

    def __unicode__(self):
        if self.show_name:
            return self.first_name + u' ' + self.last_name
        return self.username

entity_class(Profile, ['resources', 'followers', 'locations'])

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)
