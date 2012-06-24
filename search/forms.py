# -*- coding:utf-8 -*-
from django import forms

class SearchForm(forms.Form):
    surname = forms.CharField(required=False)
    country = forms.IntegerField(required=False)
    region = forms.IntegerField(required=False)
    district = forms.IntegerField(required=False)
    resource = forms.CharField(required=False)
