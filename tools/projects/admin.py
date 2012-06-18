from django.contrib import admin

from tools.projects.models import Project, ProjectIdeas

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating')
    ordering = ('-time',)

class ProjectIdeasAdmin(admin.ModelAdmin):
    list_display = ('project', 'idea')
    raw_id_fields = ('project', 'idea')

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectIdeas, ProjectIdeasAdmin)
