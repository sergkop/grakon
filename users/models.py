# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from tinymce.models import HTMLField

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

    main_location = models.ForeignKey('PersonLocation', blank=True, null=True, related_name='profiles')

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)

    # TODO: reset cache key on changing any of related data
    @cache_function(lambda args, kwargs: 'user_info/'+args[0].username, 60)
    def get_related_info(self):
        """
        Return {'profile': profile, 'locations': {person_location_id: location},
                'resources': [dict('id', 'resource', 'title', 'descr')]
        """
        data = {'profile': self}

        data['resources'] = [
                {'id': pr.id, 'resource': pr.resource,
                'title': PERSON_RESOURCE_DICT[pr.resource][0],
                'descr': PERSON_RESOURCE_DICT[pr.resource][1]}
                for pr in PersonResource.objects.filter(profile=self)
        ]

        # Prepare locations data 
        person_locations = PersonLocation.objects.filter(profile=self).values_list('id', 'location')
        loc_ids = [loc_id for id, loc_id in person_locations]
        locations_by_id = dict((loc.id, loc) for loc in Location.objects.filter(id__in=loc_ids))

        data['locations'] = dict((id, locations_by_id[loc_id]) for id, loc_id in person_locations)

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

# TODO: add subcategories
# (name, title, description)
PERSON_RESOURCES = (
    ('money', u'Деньги', u'Возможность оказать финансовую помощь'),
    ('transport', u'Транспорт', u'Возможность предоставить автомобиль, автобус, ...'),
    ('time', u'Время', u'Возможность самому принять активное участие'),
    ('printing', u'Печать', u'Наличие принтера, доступ к типографии, ...'),
    ('premises', u'Помещение', u'Ресторан, клуб, спортзал, ...'),
    ('food', u'Общественное питание', u'Поставка продуктов, обслуживание обедов'),
    ('auditory', u'Аудитория', u'Распространение информации среди своих друзей и читателей'),
    ('people', u'Человеческие ресурсы', u'Возможность предоставить волонтеров или наемных рабочих со скидкой'),
    ('organization', u'Представительство в организации', u'Руководитель общественного движения, ...'),
    ('authority', u'Представительство во власти', u'Муниципальный депутат, полицейский, ...'),
    ('other', u'Другое', u''),
)

PERSON_RESOURCE_CHOICES = [(name, title) for name, title, descr in PERSON_RESOURCES]
PERSON_RESOURCE_DICT = dict((name, (title, descr)) for name, title, descr in PERSON_RESOURCES)

# TODO: ability to add text, describing resources
class PersonResource(models.Model):
    profile = models.ForeignKey(Profile, related_name='resources')
    resource = models.CharField(u'Ресурс', max_length=20, choices=PERSON_RESOURCE_CHOICES, db_index=True)

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)

    class Meta:
        unique_together = ('profile', 'resource')

    def __unicode__(self):
        return unicode(self.profile) + ': ' + unicode(self.resource)

class PersonLocation(models.Model):
    profile = models.ForeignKey(Profile, related_name='locations')
    location = models.ForeignKey(Location, related_name='users')

    time = models.DateTimeField(auto_now=True, null=True, db_index=True)

    class Meta:
        unique_together = ('profile', 'location')

    def __unicode__(self):
        return unicode(self.profile) + ': ' + unicode(self.location)
