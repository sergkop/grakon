from django.contrib import admin

from tools.officials.models import Official

class OfficialAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'post')
    ordering = ('-time',)
    search_fields = ('last_name', 'email')

admin.site.register(Official, OfficialAdmin)
