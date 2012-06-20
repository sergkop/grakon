# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, ENTITIES_MODELS, feature_model

# TODO: avoid importing profile in many places
# TODO: user should not follow himself
class EntityParticipantManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return participants data {id: {role: {'count': count, 'ids': [top_participants_ids]}}} """
        assert 'participants' in model.features

        participants_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids, role__in=model.roles).values_list('entity_id', 'person', 'role'))

        from users.models import Profile
        participant_ratings = Profile.objects.filter(id__in=map(lambda p: p[1], participants_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            res[id] = {}
            entity_data = map(lambda p: (p[1], p[2]), filter(lambda p: p[0]==id, participants_data))

            for role in model.roles:
                profile_ids = map(lambda p: p[0], filter(lambda p: p[1]==role, entity_data))

                top_participants_rating = sorted(filter(lambda p: p[0] in profile_ids, participant_ratings),
                        key=lambda p: p[1], reverse=True)[:settings.LIST_COUNT[role]]
                res[id][role] = {
                    'count': len(profile_ids),
                    'ids': map(lambda p: p[0], top_participants_rating),
                }
        return res

    def get_related_info(self, data, ids):
        profile_ids = set(r_id for id in ids for role in data[id]['participants']
                for r_id in data[id]['participants'][role]['ids'])

        from users.models import Profile
        r_info = Profile.objects.info_for(profile_ids, related=False)

        for id in ids:
            for role in data[id]['participants']:
                data[id]['participants'][role]['entities'] = [
                        r_info[r_id] for r_id in data[id]['participants'][role]['ids'] if r_id in r_info]

    # TODO: ability to get results for a list of entity types (?)
    def participant_in(self, role, ids, entity_model):
        """ Return entities in which users participate {id: {'count': count, 'ids': [top_entities_ids]}} """
        assert 'participants' in entity_model.features

        participants_data = list(self.filter(content_type=ContentType.objects.get_for_model(entity_model),
                person__in=ids, role=role).values_list('entity_id', 'person'))

        entity_ratings = entity_model.objects.filter(id__in=map(lambda p: p[0], participants_data)) \
                .values_list('id', 'rating')

        res = {}
        for id in ids:
            entity_ids = map(lambda pd: pd[0], filter(lambda p: p[1]==id, participants_data))
            top_entity_ratings = sorted(filter(lambda er: er[0] in entity_ids, entity_ratings),
                    key=lambda er: -er[1])#[:settings.LIST_COUNT['followed']]
            res[id] = {
                'count': len(entity_ids),
                'ids': map(lambda f: f[0], top_entity_ratings),
            }
        return res

    def is_participant(self, entity, profile, role):
        assert 'participants' in type(entity).features and role in type(entity).roles
        return entity.participants.filter(person=profile, role=role).exists()

    def _add_remove(self, entity, instance, add, role, params={}):
        """ Instance corresponds to the only non-content_type foreign key of the model """
        if not self.model.fk_field:
            raise ValueError(self.model._meta.object_name+" model doesn't allow add() method")

        if self.model.feature not in type(entity).features:
            return

        if add:
            self.get_or_create(content_type=ContentType.objects.get_for_model(type(entity)),
                    entity_id=entity.id, role=role, defaults=params, **{self.model.fk_field: instance})
        else:
            # Use generic relation to filter related feature instances
            getattr(entity, self.model.feature).filter(role=role, **{self.model.fk_field: instance}) \
                    .filter(**params).delete()

        #if self.model.points_sources:
        #    from users.models import Profile
        #    profiles = [x for x in [entity, instance] if type(x) is Profile]
        #    for profile in profiles:
        #        for source in self.model.points_sources:
        #            profile.update_source_points(source)

        entity.clear_cache()
        instance.clear_cache()

    def add(self, entity, instance, role, params={}):
        self._add_remove(entity, instance, True, role, params)

    def remove(self, entity, instance, role):
        self._add_remove(entity, instance, False, role)

def get_participants(role):
    def func(entity, start=0, limit=None, sort_by=('-person__rating',)):
        assert 'participants' in type(entity).features and role in type(entity).roles

        queryset = entity.participants.order_by(*sort_by)
        return {
            'count': queryset.count(),
            'ids': queryset.values_list('person', flat=True)[slice(start, start+limit if limit else None)],
        }
    return func

# TODO: optimize it - don't get full list of ids. get count and ids separatelly, cache count
def participant_in(profile, role, entity_type):
    # Return lambda profile: {'count': count, 'entities': [top_entities_info]}
    def func(start=0, limit=None, sort_by=('-task__rating',)):
        entity_ids = list(profile.participates_in.filter(role=role,
                content_type=ContentType.objects.get_for_model(ENTITIES_MODELS[entity_type])) \
                .order_by(*sort_by).values_list('entity_id', flat=True))

        return {'count': len(entity_ids),
                'ids': entity_ids[slice(start, start+limit if limit else settings.LIST_COUNT['administered'])]}

    return func

"""
entities_data = list(profile.participates_in.filter(role=role).values_list('content_type', 'entity_id'))

entities_by_ct = {}
for ct_id, e_id in entities_data:
    entities_by_ct.setdefault(ct_id, []).append(e_id)

entities = []
for ct_id in entities_by_ct:
    model = ContentType.objects.get_for_id(ct_id).model_class()
    entities += model.objects.info_for(entities_by_ct[ct_id], related=False).values()

count = len(entities_data)
"""

ROLE_TYPES = (
    ('admin', u'Админ', u'Админы'),
    ('follower', u'Следит', u'Следят'),
    ('participant', u'Идет', u'Идут'),
)
ROLE_CHOICES = map(lambda r: (r[0], r[1]), ROLE_TYPES)

# TODO: add char field for free-text description of role
# Entity model, using this feature, must specify roles attribute - list of supported roles
@feature_model
class EntityParticipant(BaseEntityProperty):
    person = models.ForeignKey('users.Profile', related_name='participates_in')
    role = models.CharField(max_length=11, choices=ROLE_CHOICES)

    objects = EntityParticipantManager()

    feature = 'participants'
    fk_field = 'person'
    points_sources = ['contacts', 'follows'] # TODO: fix it; make it function of entity model?

    @classmethod
    def entity_methods(cls, entity_model):
        """ Assign get_follower and similar methods to entity model. Also add follower_of and similar methods to Profile. """
        methods = dict(('get_'+role, get_participants(role)) for role in entity_model.roles)

        if entity_model.entity_name == 'participants':
            for role, title in ROLE_CHOICES:
                methods[role+'_of'] = lambda profile, entity_type: participant_in(profile, role, entity_type)

        return methods

    class Meta:
        unique_together = ('content_type', 'entity_id', 'person', 'role')

    def __unicode__(self):
        return unicode(self.person) + ' is ' + self.role + ' for ' + unicode(self.entity)
