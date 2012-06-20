from django.contrib import admin

from users.models import Message, Points, Profile

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'title', 'show_email', 'time')
    ordering = ('-time',)
    search_fields = ('sender__username', 'receiver__username')
    raw_id_fields = ('sender', 'receiver')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'intro', 'about', 'rating')
    ordering = ('-add_time',)
    search_fields = ('username', 'user__email', 'first_name', 'last_name')
    raw_id_fields = ('user',)

class PointsAdmin(admin.ModelAdmin):
    list_display = ('profile', 'source', 'points', 'type')
    ordering = ('profile__username',)
    search_fields = ('profile__username', 'source')

admin.site.register(Message, MessageAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Points, PointsAdmin)
