# -*- coding:utf-8 -*-
from search.forms import SearchForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from elements.locations.widgets import LocationSelectWidget
from elements.resources.models import RESOURCE_CHOICES
from locations.models import Location
from elements.utils import table_data
from django.db.models import Q

def do_search(request):
    res_list = [] 
    for res in RESOURCE_CHOICES:
        res_list.append({"title":res[0],"value":res[1]})
    
    searchForm = SearchForm(request.GET)
    location_path = None

    if searchForm.is_valid():
        surname = searchForm.cleaned_data["surname"]
        country = searchForm.cleaned_data["country"]
        region = searchForm.cleaned_data["region"]
        district = searchForm.cleaned_data["district"]
        resource = searchForm.cleaned_data["resource"]
        location = Location.objects.get(country=None)

        if (country):
            qs=Location.objects.filter(country=country)
            if (qs.count()>0):
                location = qs[:1].get()

        if (region):
            qs = Location.objects.filter(region=region)
            if (qs.count()>0):
                location = qs[:1].get()

        if (district):
            qs = Location.objects.filter(district=district)
            if (qs.count()>0):
                location = qs[:1].get()

        #Filter by part of surname
        qfilter = Q()
        if (surname!=""):
            qfilter &= Q(last_name__icontains=surname) 

        if (resource and resource!="all" and resource!=""):
            qfilter &= Q(provided_resources__resource__icontains=resource) 
        
        #Filter by resource
        participants = location.get_entities('participants',qfilter) 
        ctx = table_data(request, 'participants', participants)

        if (country or region or district):
            location_path = location.path()

        ctx['surname']=surname
        ctx['country']=country
        ctx['region']=region
        ctx['district']=district
        ctx['resource']=resource
    else:
        participants = Location.objects.get(country=None).get_entities('participants') 
        ctx = table_data(request, 'participants', participants)

    ctx['locationWidget'] = LocationSelectWidget().render("location_select",location_path or [])
    ctx['resources'] = res_list

    return render_to_response('search.html', context_instance=RequestContext(request, ctx))
