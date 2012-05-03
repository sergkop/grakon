from django.core.management.base import NoArgsCommand

from authentication.models import ActivationProfile

class Command(NoArgsCommand):
    help = "Delete expired user registrations from the database"

    def handle_noargs(self, **options):
        ActivationProfile.objects.delete_expired_users()
