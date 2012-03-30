from django.contrib.sitemaps import Sitemap

from users.models import Profile

class ProfileSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Profile.objects.all() # TODO: take only active and verified profiles
