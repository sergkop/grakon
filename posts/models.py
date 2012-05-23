# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, BaseEntityPropertyManager, \
        entity_class, feature_model, HTMLField

OPINION_CHOICES = (
    ('positive', u'положительная'),
    ('neutral', u'нейтральная'),
    ('negative', u'негативная'),
)
OPINIONS = map(lambda op: op[0], OPINION_CHOICES)

class EntityPostManager(BaseEntityPropertyManager, BaseEntityManager):
    def get_for(self, model, ids):
        """ Return admins data {id: {'count': count, 'ids': [ids]}} """
        posts = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).select_related('profile')) # TODO: do we need select_related?

        res = {}
        for id in ids:
            entity_posts = sorted(filter(lambda p: p.entity_id==id, posts), key=lambda p: -p.rating)
            res[id] = {
                'count': len(entity_posts),
                'ids': map(lambda p: p.id, entity_posts[:settings.LIST_COUNT['posts']]),
                'entities': entity_posts[:settings.LIST_COUNT['posts']], # TODO: info dicts must be here
            }
        return res

    def get_related_info(self, data, ids):
        pass # Keep it to override BaseEntityPropertyManager.get_related_info

    def add(self, entity, profile, content, url, opinion):
        if self.model.feature not in type(entity).features:
            return

        if opinion not in OPINIONS:
            return

        # TODO: check that url is either url or ''

        #getattr(entity, self.model.feature).create(profile=profile, content=content, url=url, opinion=opinion)
        self.create(content_type=ContentType.objects.get_for_model(type(entity)),
                entity_id=entity.id, profile=profile, content=content, url=url, opinion=opinion)

        for source in self.model.points_sources:
            profile.update_source_points(source)

        entity.clear_cache()
        profile.clear_cache()

    # TODO: remove (using id)

def get_posts(entity, start=0, limit=None, sort_by=('-rating',)):
    if 'posts' not in type(entity).features:
        return None

    queryset = entity.posts.order_by(*sort_by)
    return {
        'count': queryset.count(),
        'ids': queryset.values_list('id', flat=True) \
                [slice(start, start+limit if limit else None)],
    }

# TODO: add points for posts
# TODO: introduce post type (depends on entity - officials, dmp, disqus)
@feature_model
@entity_class(['participants', 'resources'])
class EntityPost(BaseEntityModel):
    content_type = models.ForeignKey(ContentType)
    entity_id = models.PositiveIntegerField(db_index=True)
    entity = generic.GenericForeignKey('content_type', 'entity_id')

    profile = models.ForeignKey('users.Profile', related_name='post_entities')
    content = HTMLField(u'Сообщение')

    opinion = models.CharField(u'Оценка', max_length=8, choices=OPINION_CHOICES)

    objects = EntityPostManager()

    feature = 'posts'
    fk_field = 'profile'
    points_sources = [] # TODO: specify it
    entity_methods = {'get_posts': get_posts}

    entity_name = 'posts'
    cache_prefix = 'posts/'
    #table_header = 'events/table_header.html'
    #table_line = 'events/table_line.html'
    #table_cap = 'events/table_cap.html'

    roles = ['admin', 'follower']

    #def delete(self):
    #    self.entity.clear_cache()
    #    super(EntityPost, self).delete()

    #    for source in self.model.points_sources:
    #        profile.update_source_points(source)

    @models.permalink
    def get_absolute_url(self):
        return ('post', [self.id])

    def __unicode__(self):
        return 'a post by ' + unicode(self.profile)
