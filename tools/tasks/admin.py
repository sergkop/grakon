from django.contrib import admin

from tools.tasks.models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('-time',)

admin.site.register(Task, TaskAdmin)
