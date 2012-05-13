from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model

# TODO: avoid importing profile in many places
# TODO: user should not follow himself
class EntityFollowerManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return followers data {id: {'count': count, 'ids': [top_followers_ids]}} """
        followers_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'follower'))

        from users.models import Profile
        followers_rating = Profile.objects.filter(id__in=map(lambda f: f[1], followers_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            f_ids = map(lambda fd: fd[1], filter(lambda f: f[0]==id, followers_data))
            top_followers_rating = sorted(filter(lambda f: f[0] in f_ids, followers_rating),
                    key=lambda f: f[1], reverse=True)[:settings.LIST_COUNT['followers']]
            res[id] = {
                'count': len(f_ids),
                'ids': map(lambda f: f[0], top_followers_rating),
            }
        return res

    def followed(self, ids, entity_model):
        """ Return entities followed by users {id: {'count': count, 'ids': [top_followed_ids]}} """
        followed_data = list(self.filter(content_type=ContentType.objects.get_for_model(entity_model),
                follower__id__in=ids).values_list('entity_id', 'follower'))

        followed_rating = entity_model.objects.filter(id__in=map(lambda f: f[0], followed_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            e_ids = map(lambda fd: fd[0], filter(lambda f: f[1]==id, followed_data))
            top_followed_rating = sorted(filter(lambda f: f[0] in e_ids, followed_rating),
                    key=lambda f: f[1], reverse=True)[:settings.LIST_COUNT['followed']]
            res[id] = {
                'count': len(e_ids),
                'ids': map(lambda f: f[0], top_followed_rating),
            }
        return res

    def is_followed(self, entity, profile):
        if self.model.feature not in type(entity).features:
            return False
        return getattr(entity, self.model.feature).filter(follower=profile).exists()

@feature_model
class EntityFollower(BaseEntityProperty):
    follower = models.ForeignKey('users.Profile', related_name='followed_entities')

    objects = EntityFollowerManager()

    feature = 'followers'
    fk_field = 'follower'
    points_sources = ['contacts', 'follows']

    class Meta:
        unique_together = ('content_type', 'entity_id', 'follower')

    def __unicode__(self):
        return unicode(self.follower) + ' follows ' + unicode(self.entity)
