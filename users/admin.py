from django.contrib import admin

from users.models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'show_name')
    ordering = ('username',)
    search_fields = ('username', 'user__email', 'first_name', 'last_name')
    raw_id_fields = ('user', 'main_location')

admin.site.register(Profile, ProfileAdmin)
