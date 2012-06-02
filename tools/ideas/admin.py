from django.contrib import admin

from tools.ideas.models import Idea

class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('-time',)

admin.site.register(Idea, IdeaAdmin)
