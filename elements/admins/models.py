from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model

# TODO: similar to follower model code
class EntityAdminManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return admins data {id: {'count': count, 'ids': [ids]}} """
        admins_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'admin'))

        from users.models import Profile
        admins_rating = Profile.objects.filter(id__in=map(lambda a: a[1], admins_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            a_ids = map(lambda ad: ad[1], filter(lambda a: a[0]==id, admins_data))
            top_admin_rating = sorted(filter(lambda a: a[0] in a_ids, admins_rating),
                    key=lambda a: a[1], reverse=True)[:settings.LIST_COUNT['admins']]
            res[id] = {
                'count': len(a_ids),
                'ids': map(lambda a: a[0], top_admin_rating),
            }
        return res

    def is_admin(self, entity, profile):
        if self.model.feature not in type(entity).features:
            return False
        return getattr(entity, self.model.feature).filter(admin=profile).exists()

    # TODO: take params for pagination
    def administered_by(self, profile):
        """ Return {'count': count, 'entities': [top_entities_info]} """
        entities_data = list(profile.administered_entities.values_list('content_type', 'entity_id'))

        entities_by_ct = {}
        for ct_id, e_id in entities_data:
            entities_by_ct.setdefault(ct_id, []).append(e_id)

        entities = []
        for ct_id in entities_by_ct:
            model = ContentType.objects.get_for_id(ct_id).model_class()
            entities += model.objects.info_for(entities_by_ct[ct_id], related=False).values()

        return {'count': len(entities_data),
                'entities': sorted(entities, key=lambda e: -e['instance'].rating)[:settings.LIST_COUNT['admins']]}

@feature_model
class EntityAdmin(BaseEntityProperty):
    admin = models.ForeignKey('users.Profile', related_name='administered_entities')

    objects = EntityAdminManager()

    feature = 'admins'
    fk_field  = 'admin'
    points_sources = ['admin']

    class Meta:
        unique_together = ('content_type', 'entity_id', 'admin')

    def __unicode__(self):
        return unicode(self.admin) + ' is admin of ' + unicode(self.entity)
