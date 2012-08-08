from django.contrib import admin

from referendum.models import InitiativeGroup, Question

class InitiativeGroupAdmin(admin.ModelAdmin):
    list_display = ('location',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(InitiativeGroup, InitiativeGroupAdmin)
admin.site.register(Question, QuestionAdmin)
