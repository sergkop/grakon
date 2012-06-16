# -*- coding:utf-8 -*-
from django import forms

#from elements.resources.forms import resources_init
from tools.ideas.models import Idea

#@resources_init
class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ('title', 'description')
