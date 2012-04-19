# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models

from tinymce.models import HTMLField

from elements.models import BaseEntityManager, entity_class, EntityLocation
from elements.utils import reset_cache
from locations.models import Location
from services.cache import cache_function

class ProfileManager(BaseEntityManager):
    def get_info(self, data):
        ids = data.keys()

        # TODO: 'locations': EntityLocation.objects.for_entity(self),
        # TODO: 'follows': list(self.followed_entities.values_list('id', flat=True)),

        profiles_by_id = dict((p.id, p) for p in Profile.objects.filter(id__in=ids))
        for id in ids:
            if id in profiles_by_id:
                data[id]['profile'] = profiles_by_id[id]
            else:
                del data[id] # TODO: do we need it?

    def for_location(self, location, start=0, limit=None, sort_by='points'):
        pass # TODO: write it

BaseProfile = entity_class('Profile', ['resources', 'skills', 'followers'])
class Profile(BaseProfile):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)

    first_name = models.CharField(u'Имя', max_length=40)
    last_name = models.CharField(u'Фамилия', max_length=40)
    show_name = models.BooleanField(u'Показывать настоящее имя', default=False,
            help_text=u'<b>Поставьте эту галку, чтобы другие пользователи видели ваше настоящее имя</b>')

    about = HTMLField(u'О себе', default='', blank=True)

    main_location = models.ForeignKey(EntityLocation, blank=True, null=True, related_name='profiles')

    objects = ProfileManager()

    cache_prefix = 'user_info/'

    def calc_points(self):
        pass # TODO: implement it

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.username])

    def __unicode__(self):
        # TODO: fix it
        if self.show_name and self.first_name and self.last_name:
            return u'%s %s (%s)' % (self.first_name, self.last_name, self.username)
        return self.username

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)
