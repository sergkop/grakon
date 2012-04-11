# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from tinymce.models import HTMLField

from elements.models import BaseEntityProperty, EntityLocation, EntityResource
from locations.models import Location
from services.cache import cache_function

class Profile(models.Model):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)

    first_name = models.CharField(u'Имя', max_length=40)
    last_name = models.CharField(u'Фамилия', max_length=40,
            help_text=u'<b>Мы не будем показывать ваше настоящее имя другим пользователям без вашего разрешения.</b>')
    show_name = models.BooleanField(u'Показывать настоящее имя', default=False,
            help_text=u'<b>Поставьте эту галку, чтобы другие пользователи видели ваше настоящее имя</b>')

    about = HTMLField(u'О себе', default='', blank=True)

    main_location = models.ForeignKey(EntityLocation, blank=True, null=True, related_name='profiles')

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)

    # TODO: reset cache key on changing any of related data
    @cache_function(lambda args, kwargs: 'user_info/'+args[0].username, 60)
    def get_related_info(self):
        """
        Return {'profile': profile, 'locations': {person_location_id: location},
                'resources': resources}
        """
        data = {
            'profile': self,
            'resources': list(EntityResource.objects.for_entity(self)),
            'locations': EntityLocation.objects.for_entity(self),
        }

        # Follows
        follows = FollowedEntity.objects.filter(follower=self)

        # Followers
        followers = FollowedEntity.objects.for_entity(self)

        return data

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

class FollowedEntity(BaseEntityProperty):
    follower = models.ForeignKey(Profile, related_name='followed_entities')

    class Meta:
        unique_together = ('content_type', 'entity_id', 'follower')

    def __unicode__(self):
        return unicode(self.follower) + ' follows ' + unicode(self.entity)
