from django.contrib import admin

from users.models import PersonLocation, PersonResource, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'show_name')
    ordering = ('username',)
    search_fields = ('username', 'user__email', 'first_name', 'last_name')
    raw_id_fields = ('user', 'main_location')

class PersonResourceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'resource')
    ordering = ('profile__username',)
    search_fields = ('profile__username', 'resource')
    raw_id_fields = ('profile',)

class PersonLocationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'location')
    ordering = ('profile__username',)
    search_fields = ('profile__username', 'location__id', 'location__name')
    raw_id_fields = ('profile', 'location')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(PersonResource, PersonResourceAdmin)
admin.site.register(PersonLocation, PersonLocationAdmin)
