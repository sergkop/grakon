RESOURCES = {{ resources|safe }};

RESOURCES_DICT = {};
_.each(RESOURCES, function(resource){
    RESOURCES_DICT[resource[0]] = resource[1];
});

GET_SUBREGIONS_URL = "{{ get_subregions_url|safe }}";
