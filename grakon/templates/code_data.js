RESOURCES = {{ resources|safe }};

RESOURCES_DICT = {};
_.each(RESOURCES, function(resource){
    RESOURCES_DICT[resource[0]] = resource[1];
});

GET_SUBREGIONS_URL = "{% url get_subregions %}";
REMOVE_LOCATION_URL = "{% url remove_location %}";
UPDATE_TEXT_FIELD = "{% url update_text_field %}";
