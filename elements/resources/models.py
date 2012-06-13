# -*- coding:utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model
from elements.utils import reset_cache

# (name, title)
RESOURCE_CHOICES = (
    ('money', u'спонсор/деньги'),
    ('time', u'волонтер/время'),
    ('transport', u'автомобиль/автобус'),
    ('printing', u'типография/печать'),
    ('premises', u'помещение/заведение'),
    ('food', u'повар/общественное питание'),

    ('authority', u'представитель власти'),
    ('organization', u'представитель большой организации'),

    ('lawyer', u'юрист/адвокат/правозащитник'),
    ('journalist', u'журналист/представитель СМИ'),
    ('observer', u'опыт наблюдения на выборах'),
    ('design', u'дизайнер/художник/оформитель'),
    ('programmer', u'программист/веб-разработчик'),
    ('copywriting', u'копирайтер/писатель/поэт'),
    ('photographer', u'фотограф/оператор/монтажер'),
    ('organizator', u'организатор мероприятий'),
    ('computer', u'продвинутый пользователь компьютера'),
    ('pr', u'PR специалист/специалист по продвижению'),
    ('creative', u'креативщик/генератор идей/нэймер'),
    ('musician', u'музыкант/певец/диджей'),
    ('narrator', u'оратор/ведущий/диктор'),
    ('actor', u'актер/шоумэн'),
    ('interpreter', u'переводчик'),
    ('strong', u'физическая сила'),
    ('auditory', u'большое количество друзей'),

    #('people', u'Человеческие ресурсы'), #u'Возможность предоставить волонтеров или наемных рабочих со скидкой'),
    # учитель/преподаватель
    #('other', u'Другое', u''),
)

RESOURCE_DICT = dict((name, title) for name, title in RESOURCE_CHOICES)

# TODO: take entity model parameter, which specifies the necessaty of provider value
class EntityResourceManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return {id: {provider_id: {'name': name, 'title': title, 'description': description}}} """
        res = dict((id, {}) for id in ids)

        resources_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'resource', 'description', 'provider'))

        # TODO: sort by provider and by resource
        for id, resource, descr, provider_id in resources_data:
            resource_data = {'name': resource, 'title': RESOURCE_DICT[resource], 'description': descr}
            res[id].setdefault(provider_id if provider_id else 'none', {'data': []})['data'].append(resource_data)

        return res

    def _add_remove(self, entity, resource, add, description='', provider=None):
        if self.model.feature not in type(entity).features:
            return

        if resource not in RESOURCE_DICT.keys():
            return

        if add:
            entity_resource, created = self.get_or_create(content_type=ContentType.objects.get_for_model(type(entity)),
                    entity_id=entity.id, resource=resource, provider=provider, defaults={'description': description})
            if not created:
                entity_resource.description = description
                entity_resource.save()
        else:
            # Use generic relation to filter related feature instances
            getattr(entity, self.model.feature).filter(resource=resource, provider=provider).delete()

        #if self.model.points_sources:
        #    from users.models import Profile
        #    profiles = [x for x in [entity, provider] if type(x) is Profile]
        #    for profile in profiles:
        #        for source in self.model.points_sources:
        #            profile.update_source_points(source)

        entity.clear_cache()
        if provider:
            provider.clear_cache()

    def add_or_update(self, entity, resource, description='', provider=None):
        self._add_remove(entity, resource, True, description, provider)

    def remove(self, entity, resource, provider=None):
        self._add_remove(entity, resource, False, provider=provider)

    # TODO: update resources with descriptions
    def update(self, entity, resources):
        if self.model.feature not in type(entity).features:
            return

        # Filter out resources not from the list
        resources = set(RESOURCE_DICT.keys()) & set(resources)

        entity_resources = list(getattr(entity, self.model.feature).all())
        new_resources = resources - set(er.resource for er in entity_resources)

        for er in entity_resources:
            if er.resource not in resources:
                er.delete()

        # TODO: this can cause IntegrityError
        self.bulk_create([self.model(entity=entity, resource=resource) for resource in new_resources])

        from users.models import Profile
        if type(entity) is Profile:
            entity.update_source_points('resources')

        entity.clear_cache()

@reset_cache
def update_resources(entity, resources):
    EntityResource.objects.update(entity, resources)

# TODO: add 'other' option for resource type
@feature_model
class EntityResource(BaseEntityProperty):
    resource = models.CharField(u'Ресурс', max_length=20, choices=RESOURCE_CHOICES, db_index=True)
    description = models.CharField(u'Описание', max_length=140, blank=True)
    provider = models.ForeignKey('users.Profile', blank=True, null=True, related_name='provided_resources')

    objects = EntityResourceManager()

    feature = 'resources'
    points_sources = ['resources']
    entity_methods = {'update_resources': update_resources}

    class Meta:
        unique_together = ('content_type', 'entity_id', 'resource', 'provider')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.resource)
