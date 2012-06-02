from django.contrib import admin

from tools.projects.models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('-time',)

admin.site.register(Project, ProjectAdmin)
