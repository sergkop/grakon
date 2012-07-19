from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import dateformat

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model

class EntityCommentManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        res = {}

        comments = self.filter(content_type=ContentType.objects.get_for_model(model), entity_id__in=ids)

        from users.models import Profile
        profiles = Profile.objects.only('id', 'first_name', 'last_name') \
                .in_bulk(set(c.person_id for c in comments))

        for id in ids:
            count = 0
            comments_by_parent = {}
            for comment in filter(lambda c: c.entity_id==id, comments):
                comments_by_parent.setdefault(comment.parent_id, []).append(comment)
                count += 1

            # Sort comments by time
            for parent_id in comments_by_parent:
                comments_by_parent[parent_id] = sorted(comments_by_parent[parent_id],
                        key=lambda c: c.time, reverse=True)

            def get_comment_data(comment):
                profile = profiles[comment.person_id]
                return {
                    'comment': {
                        'comment_id': comment.id,
                        'ct_id': comment.content_type_id,
                        'entity_id': comment.entity_id,
                        'comment': comment.comment,
                        'time': dateformat.format(comment.time, 'j b Y'),
                    },
                    'author': {
                        'id': profile.id,
                        'full_name': unicode(profile),
                        'url': profile.get_absolute_url(),
                    },
                    'children': [get_comment_data(child) for child in comments_by_parent.get(comment.id, [])],
                }

            res[id] = {
                'count': count,
                'data': [get_comment_data(comment) for comment in comments_by_parent.get(None, [])],
            }
        return res

    def add(self, entity, profile, comment, parent_id=None):
        if self.model.feature not in type(entity).features:
            return

        parent = None
        if parent_id:
            try:
                parent = self.get(id=parent_id)
            except self.model.DoesNotExist:
                pass

        self.create(content_type=ContentType.objects.get_for_model(type(entity)),
                entity_id=entity.id, person=profile, comment=comment, parent=parent)

        entity.clear_cache()
        profile.clear_cache()

    def remove(self, entity, profile, comment_id):
        if self.model.feature not in type(entity).features:
            return

        getattr(entity, self.model.feature).filter(person=profile, id=comment_id).delete()

        entity.clear_cache()
        profile.clear_cache()

@feature_model
class EntityComment(BaseEntityProperty):
    person = models.ForeignKey('users.Profile', related_name='comments')
    parent = models.ForeignKey('self', blank=True, null=True)
    comment = models.TextField()

    objects = EntityCommentManager()

    feature = 'comments'

    def __unicode__(self):
        return unicode(self.person) + ' commented on ' + unicode(self.entity)
