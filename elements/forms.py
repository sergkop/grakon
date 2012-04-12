# -*- coding:utf-8 -*-
from django import forms
from django.template.loader import render_to_string

from crispy_forms.layout import HTML

from locations.models import Location

# TODO: set path
LocationHTML = HTML(
    '<div id="location_select">'+render_to_string('elements/select_location.html')+'</div>' \
    '<script type="text/javascript">' \
        '$().ready(function(){' \
                '(new SelectLocation({el: $("#location_select"), path: []})).render();' \
            '});' \
    '</script>'
)

class LocationForm(forms.Form):
    def __init__(self, required, label):
        """ If required then the lowest possible level must be chosen """
        super(LocationForm, self).__init__()
        self.required = required

        self.fields.update({
            'region': forms.CharField(label=label, required=False),
            'district': forms.CharField(required=False),
            'location': forms.CharField(required=False),
        )

        # TODO: set path on errors

    def clean(self):
        msg = u'Необходимо выбрать нижний уровень географической иерархии'

        try:
            self.location = Location.objects.get(id=int(self.cleaned_data.get('location', '')))
        except (ValueError, Location.DoesNotExist):
            try:
                self.location = Location.objects.get(id=int(self.cleaned_data.get('district', '')))
            except (ValueError, Location.DoesNotExist):
                try:
                    self.location = Location.objects.get(id=int(self.cleaned_data.get('region', '')))
                except (ValueError, Location.DoesNotExist):
                    if self.required:
                        raise forms.ValidationError(msg)
                    else:
                        self.location = Location.objects.country()

        if self.required:
            if self.location.region_id is None:
                raise forms.ValidationError(msg)

            # Check that this is the lowest possible level
            if self.location.is_district():
                if Location.objects.filter(district=self.location).count() == 0:
                    raise forms.ValidationError(msg)

        return self.cleaned_data
