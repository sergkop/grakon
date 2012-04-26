from django.contrib import admin

from users.models import Points, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'show_name', 'rating')
    ordering = ('username',)
    search_fields = ('username', 'user__email', 'first_name', 'last_name')
    raw_id_fields = ('user',)

class PointsAdmin(admin.ModelAdmin):
    list_display = ('profile', 'source', 'points', 'type')
    ordering = ('profile__username',)
    search_fields = ('profile__username', 'source')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Points, PointsAdmin)
