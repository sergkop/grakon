from django.db import models

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model

class EntityCommentManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        res = {}
        for id in ids:
            res[id] = {}
        return res

    def add(self, entity, profile, comment, parent_id=None):
        if self.model.feature not in type(entity).features:
            return

        # TODO: add parent if provided
        self.create(content_type=ContentType.objects.get_for_model(type(entity)),
                entity_id=entity.id, person=profile, comment=comment)

        # TODO: reset caches

    def remove(self, entity, profile, comment_id):
        pass

@feature_model
class EntityComment(BaseEntityProperty):
    person = models.ForeignKey('users.Profile', related_name='comments')
    parent = models.ForeignKey('self', blank=True, null=True)
    comment = models.TextField()

    objects = EntityCommentManager()

    feature = 'comments'

    def __unicode__(self):
        return unicode(self.person) + ' commented on ' + unicode(self.entity)
