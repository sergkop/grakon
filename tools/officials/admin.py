from django.contrib import admin

from tools.officials.models import Official

class OfficialAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name', 'post')
    ordering = ('last_name',)
    search_fields = ('last_name', 'email')

admin.site.register(Official, OfficialAdmin)
