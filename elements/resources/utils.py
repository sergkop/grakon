# -*- coding:utf-8 -*-
from elements.resources.data import RESOURCE_DICT

def entity_object_action(func):
    """
    Декоратор действий над объектом entity.
    Проверяет валидность действия и обновляет кэш и рейтинг
    """
    def wrapper(self, entity, resource, provider=None, *args, **kwargs):
        if not resource:
            return u'Не указан ресурс'

        if self.model.feature not in type(entity).features:
            return u'К модели нельзя прикрепить ресурс'

        if type(entity).entity_name != 'projects':
            if resource not in RESOURCE_DICT.keys():
                return u'Ресурс должен быть в списке разрешенных'

        result = func(self, entity, resource, provider=provider, *args, **kwargs) # само выполнение декорированного метода

        entity.clear_cache()
        if provider:
            provider.clear_cache()

        entity.update_rating()
        if entity.entity_name == 'ideas':
            entity.task.update_rating()

        return result

    return wrapper
