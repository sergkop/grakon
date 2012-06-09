from django.db import models
from django.contrib.contenttypes.models import ContentType

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model
from locations.models import Location

class EntityLocationManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return {id: {'ids': loc_ids, 'main_id': loc_id_or_None}} """
        locations_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'location', 'is_main'))

        res = {}
        for id in ids:
            entity_locations = filter(lambda el: el[0]==id, locations_data)
            res[id] = {'ids': map(lambda el: el[1], entity_locations)}

            main_locations = filter(lambda el: el[2], entity_locations)
            res[id]['main_id'] = main_locations[0][1] if main_locations else None
        return res

    def get_related_info(self, data, ids):
        super(EntityLocationManager, self).get_related_info(data, ids)

        for id in ids:
            id_data = data[id][self.model.feature]
            id_data['main'] = (filter(lambda d: d['instance'].id==id_data['main_id'],
                    id_data['entities']) or [None])[0]

    def update_location(self, entity, location):
        # TODO: what if there are several locations? what about main?
        el = self.filter(content_type=ContentType.objects.get_for_model(type(entity)),
                entity_id=entity.id)[0]
        el.location = location
        el.save()

# TODO: some models may need only one location (?)
# TODO: reset cache on save()/delete() (here and in other models)
@feature_model
class EntityLocation(BaseEntityProperty):
    location = models.ForeignKey(Location, related_name='entities')
    is_main = models.BooleanField(default=False, db_index=True)

    objects = EntityLocationManager()

    feature = 'locations'
    fk_field = 'location'

    class Meta:
        unique_together = ('content_type', 'entity_id', 'location')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.location)
