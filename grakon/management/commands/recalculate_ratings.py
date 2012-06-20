from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Recalculate ratings of entity models."

    def handle(self, *args, **options):
        from elements.models import ENTITIES_MODELS
        for model in ENTITIES_MODELS.values():
            for instance in model.objects.all():
                instance.update_rating()
