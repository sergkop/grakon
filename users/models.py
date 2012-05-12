# -*- coding:utf-8 -*-
import inspect

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, ENTITIES_MODELS, \
        entity_class, EntityAdmin, EntityFollower, EntityResource, HTMLField

class ProfileManager(BaseEntityManager):
    def get_info(self, data, ids):
        # TODO: add info on non-profile entities followed by the user

        # Get contacts
        contacts = EntityFollower.objects.followed(ids, Profile)
        for id in ids:
            data[id]['contacts'] = contacts[id]

        # Get user points
        for id in ids:
            data[id]['points'] = {'online': 0, 'offline': 0, 'leader': 0}

        points_data = Points.objects.filter(profile__id__in=ids).values_list('profile', 'type', 'points')

        for id, type, points in points_data:
            data[id]['points'][type] += points

    def get_related_info(self, data, ids):
        contacts_ids = set(c_id for id in ids for c_id in data[id]['contacts']['ids'])
        contacts_info = Profile.objects.info_for(contacts_ids, related=False)
        for id in ids:
            data[id]['contacts']['entities'] = [contacts_info[c_id] for c_id in data[id]['contacts']['ids']
                            if c_id in contacts_info]

@entity_class(['resources', 'followers', 'locations'])
class Profile(BaseEntityModel):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30, db_index=True)

    first_name = models.CharField(u'Имя', max_length=40)
    last_name = models.CharField(u'Фамилия', max_length=40)
    show_name = models.BooleanField(u'Показывать настоящее имя', default=True,
            help_text=u'Снимите эту галку, чтобы скрыть свое имя от других пользователей')

    about = HTMLField(u'О себе', default='', blank=True)

    objects = ProfileManager()

    entity_name = 'participants'
    cache_prefix = 'user_info/'
    table_header = 'profiles/table_header.html'
    table_line = 'profiles/table_line.html'

    def calc_rating(self):
        pass # TODO: implement it

    # TODO: make it admin interface command
    def update_points(self):
        # TODO: create celery task
        Points.objects.recalculate(self)

    # TODO: take bool parameter whether to run it in background
    def update_source_points(self, source):
        # TODO: create celery task
        Points.objects.recalculate_source(self, source)

    def has_contact(self, profile):
        return EntityFollower.objects.is_followed(profile, self)

    def save(self):
        super(Profile, self).save()
        self.update_points()
        self.clear_cache()

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.username])

    def full_name(self):
        return self.first_name + u' ' + self.last_name

    def __unicode__(self):
        return self.full_name() if self.show_name else self.username

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)

def points_type(type):
    """ type is 'online', 'offline' or 'leader' """
    def decorator(func):
        func.type = type
        return func
    return decorator

def features_points(queryset, points_dict):
    """ Shortcut to calculate points based on the number of entity feature instances """
    # TODO: use aggregates to get counts immediately?
    entities = list(queryset.values_list('content_type', 'entity_id'))

    entities_by_ct = {}
    for ct_id, entity_id in entities:
        entities_by_ct.setdefault(ct_id, []).append(entity_id)

    res = 0
    for entity_type in points_dict:
        entity_ct_id = ContentType.objects.get_for_model(ENTITIES_MODELS[entity_type]).id
        entities_num = len(entities_by_ct.get(entity_ct_id, []))
        res += entities_num * points_dict[entity_type]

    return res

# TODO: give points for being admin
# TODO: complaints related to user lower his points
# Collection of methods for calculating profile points coming from different sources
class PointsSources(object):
    @points_type('online')
    def registration(self, profile):
        return 3

    # TODO: rename it
    @points_type('online')
    def show_name(self, profile):
        res = 3 if profile.show_name else 0
        res += 1 if profile.about else 0
        return res

    # TODO: do we need it since resources became mandatory?
    @points_type('online')
    def resources(self, profile):
        has_resources = profile.resources.exists()
        return 3 if has_resources else 0

    @points_type('online')
    def follows(self, profile):
        points = {'officials': 1}
        return features_points(EntityFollower.objects.filter(follower=profile), points)

    @points_type('online')
    def contacts(self, profile):
        contacts_ids = list(EntityFollower.objects.filter(follower=profile,
                content_type=ContentType.objects.get_for_model(Profile)).values_list('entity_id', flat=True))
        followers_ids = list(EntityFollower.objects.filter(entity_id=profile.id,
                content_type=ContentType.objects.get_for_model(Profile)).values_list('follower', flat=True))

        # TODO: several levels (5 contacts, 10, 50) + count 2-sided connections
        # TODO: distinguish the limit when a popular person is followed by many

        res = 0
        if len(contacts_ids) > 0:
            res += 1
        if len(followers_ids) >= 10:
            res += 3
        return res

    @points_type('online')
    def admin(self, profile):
        points = {'officials': 3}
        return features_points(EntityAdmin.objects.filter(admin=profile), points)

points_methods = PointsSources()

# [sources]
POINTS_SOURCES = map(lambda m: m[0], inspect.getmembers(points_methods, inspect.ismethod))

# {source: type}
SOURCES_TYPES = dict((source, getattr(points_methods, source).type) for source in POINTS_SOURCES)

POINTS_TYPES = (('online', u'Онлайн'), ('offline', u'Оффлайн'), ('leader', u'Лидерство'))

class PointsManager(models.Manager):
    def recalculate(self, profile):
        points_by_source = dict((p.source, p) for p in self.filter(profile=profile))

        to_delete = []
        to_create = []
        for source in POINTS_SOURCES:
            points = getattr(points_methods, source)(profile)

            if points != 0:
                if source in points_by_source:
                    if points_by_source[source].points != points:
                        to_delete.append(points_by_source[source].id)
                        to_create.append(Points(profile=profile, source=source, points=points,
                                type=SOURCES_TYPES[source]))
                else:
                    to_create.append(Points(profile=profile, source=source, points=points,
                            type=SOURCES_TYPES[source]))
            else:
                if source in points_by_source:
                    to_delete.append(points_by_source[source].id)

        self.filter(id__in=to_delete).delete()

        # TODO: this can cause IntegrityError
        self.bulk_create(to_create)

        profile.clear_cache()

    def recalculate_source(self, profile, source):
        points = getattr(points_methods, source)(profile)

        if points != 0:
            p, created = Points.objects.get_or_create(profile=profile, source=source,
                    defaults={'points': points})
            if not created:
                if p.points != points:
                    p.points = points
                    p.save()
        else:
            Points.objects.filter(profile=profile, source=source).delete()

        profile.clear_cache()

class Points(models.Model):
    profile = models.ForeignKey(Profile)
    source = models.CharField(max_length=15, db_index=True)
    points = models.IntegerField(u'Очки', default=0)
    type = models.CharField(max_length=7, choices=POINTS_TYPES)

    objects = PointsManager()

    class Meta:
        unique_together = ('profile', 'source')

def set_points_type(sender, instance, **kwargs):
    instance.type = SOURCES_TYPES[instance.source]

models.signals.pre_save.connect(set_points_type, sender=Points)

class Message(models.Model):
    sender = models.ForeignKey(Profile, verbose_name=u'Отправитель', related_name='sent_messages')
    receiver = models.ForeignKey(Profile, verbose_name=u'Получатель', related_name='received_messages')
    title = models.CharField(u'Тема', max_length=100)
    body = models.TextField(u'Сообщение')
    show_email = models.BooleanField(u'Показать email получателю', default=False)
    time = models.DateTimeField(auto_now=True)
