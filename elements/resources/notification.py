from elements.resources.data import RESOURCE_DICT
from elements.resources.models import EntityResource
from notifications.models import NotificationType, register_notification

@register_notification
class NewResourceNotification(NotificationType):
    """ data = resource_id """
    name = 'new_resource'
    template = 'notifications/new_resource.html'

    @classmethod
    def recipients(cls, data):
        # TODO: what if this resource doesn't exist anymore?
        resource_id = data
        resource = EntityResource.objects.get(id=resource_id)

        res = []
        entity = resource.entity

        if entity.entity_name == 'ideas':
            idea = entity
            task_info = idea.task.info(related=True)

            # Creators of idea
            res += [idea_admin['id'] for idea_info in task_info['ideas']['entities']
                    for idea_admin in idea_info['participants']['admin']['entities']]

            # Providers of idea resources
            res += [provider for idea_info in task_info['ideas']['entities']
                    for provider in idea_info['resources'].keys()]

            # Creator of task
            res += [e['id'] for e in task_info['participants']['admin']['entities']]

            # Followers of task
            res += [e['id'] for e in task_info['participants']['follower']['entities']]

            # Exclude provider of resource
            res = set(res) - {idea.info(related=False)['participants']['admin']['entities'][0]['id']}

        elif entity.entity_name == 'projects' and resource.provider_id:
            project = entity
            project_info = project.info(related=True)

            # Creator of project
            res += [project_info['participants']['admin']['entities'][0]['id']]

            # Followers of project
            res += [e['id'] for e in project_info['participants']['follower']['entities']]

            # Providers of project resources
            res += list(set(project_info['resources'].keys()) - {'none'})

            res = set(res) - {resource.provider_id}

        return res

    @classmethod
    def context(cls, data):
        resource_id = data
        resource = EntityResource.objects.get(id=resource_id)

        ctx = {'resource': resource}

        if resource.entity.entity_name == 'ideas':
            ctx['resource_title'] = RESOURCE_DICT[resource.resource]
        elif resource.entity.entity_name == 'projects' and resource.provider_id:
            ctx['resource_title'] = resource.resource

        return ctx
