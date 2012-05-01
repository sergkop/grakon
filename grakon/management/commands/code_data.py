from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Create code_data.js at a given path"

    def handle(self, *args, **options):
        from grakon.views import code_data
        with open(args[0], 'w') as f:
            f.write(code_data(None).content)
