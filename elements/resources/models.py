# -*- coding:utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model
from elements.resources.data import RESOURCE_DICT, RESOURCE_CHOICES
from elements.resources.utils import entity_object_action
from elements.utils import reset_cache


# TODO: take entity model parameter, which specifies the necessaty of provider value
class EntityResourceManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return {id: {provider_id: {'name': name, 'title': title, 'description': description}}} """
        res = dict((id, {}) for id in ids)

        resources_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'resource', 'description', 'provider'))

        # Get all related profiles
        from users.models import Profile
        profiles_by_id = Profile.objects.only('id', 'username', 'first_name', 'last_name', 'intro', 'rating') \
                .in_bulk(set(r[3] for r in resources_data))

        # TODO: sort by provider and by resource
        for id, resource, descr, provider_id in resources_data:
            resource_data = {'name': resource, 'description': descr}
            if model.entity_name == 'projects':
                resource_data['title'] = resource
            else:
                resource_data['title'] = RESOURCE_DICT[resource]

            res[id].setdefault(provider_id if provider_id else 'none', {'data': []})['data'].append(resource_data)

        for id in ids:
            for p_id in res[id]:
                if p_id != 'none':
                    profile = profiles_by_id[p_id]
                    res[id][p_id]['provider'] = {
                        'id': profile.id,
                        'url': profile.get_absolute_url(),
                        'full_name': unicode(profile),
                    }

        return res

    def get_related_info(self, data, ids):
        pass

    @entity_object_action
    def add(self, entity, resource, provider=None, description=''):
        """ Создает или обновляет ресурс, привязанный к сущности """
        entity_resource, created = self.get_or_create(content_type=ContentType.objects.get_for_model(type(entity)),
            entity_id=entity.id, resource=resource, provider=provider, defaults={'description': description})

        if not created:
            entity_resource.description = description
            entity_resource.save()

    @entity_object_action
    def remove(self, entity, resource, provider=None):
        """ Удаляет ресурс, привязанный к сущности """
        getattr(entity, self.model.feature).filter(resource=resource, provider=provider).delete()


    def edit(self, entity, old_resource, new_resource, provider=None, description=''):
        """ Удаляет, потом создает ресурс, привязанный к сущности """
        self.remove(entity, old_resource, provider=provider)
        self.add(entity, new_resource, provider=provider, description=description)

    # Used in registration form
    def update(self, entity, resources):
        if self.model.feature not in type(entity).features:
            return

        # Filter out resources not from the list
        if type(entity).entity_name != 'projects':
            resources = set(RESOURCE_DICT.keys()) & set(resources)

        entity_resources = list(getattr(entity, self.model.feature).all())
        new_resources = resources - set(er.resource for er in entity_resources)

        for er in entity_resources:
            if er.resource not in resources:
                er.delete()

        # TODO: this can cause IntegrityError
        self.bulk_create([self.model(entity=entity, resource=resource) for resource in new_resources])

        entity.clear_cache()

@reset_cache
def update_resources(entity, resources):
    EntityResource.objects.update(entity, resources)

# TODO: add 'other' option for resource type
@feature_model
class EntityResource(BaseEntityProperty):
    resource = models.CharField(u'Ресурс', max_length=100, db_index=True)
    description = models.CharField(u'Описание', max_length=140, blank=True)
    provider = models.ForeignKey('users.Profile', blank=True, null=True, related_name='provided_resources')

    objects = EntityResourceManager()

    feature = 'resources'
    entity_methods = {'update_resources': update_resources}

    class Meta:
        unique_together = ('content_type', 'entity_id', 'resource', 'provider')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.resource)
