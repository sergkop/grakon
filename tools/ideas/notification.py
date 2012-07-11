from notifications.models import NotificationType, register_notification
from tools.ideas.models import Idea

@register_notification
class NewIdeaNotification(NotificationType):
    """ data = idea_id """
    name = 'new_idea'
    template = 'notifications/new_idea.html'

    @classmethod
    def recipients(cls, data):
        # TODO: what if this idea doesn't exist anymore?
        idea_id = data
        idea = Idea.objects.select_related('task').get(id=idea_id)

        new_idea_info = idea.info(related=False)
        task_info = idea.task.info(related=True)

        res = []

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

        # Exclude creator of the idea
        res = set(res) - {new_idea_info['participants']['admin']['entities'][0]['id']}

        return res

    @classmethod
    def context(cls, data):
        idea_id = data
        idea = Idea.objects.select_related('task').get(id=idea_id)
        return {'idea_info': idea.info(related=False), 'task': idea.task}
