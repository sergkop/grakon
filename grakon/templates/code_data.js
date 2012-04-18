RESOURCES = {{ resources|safe }};

RESOURCES_DICT = {};
_.each(RESOURCES, function(resource){
    RESOURCES_DICT[resource[0]] = resource[1];
});

SKILLS = {{ skills|safe }};

SKILLS_DICT = {};
_.each(SKILLS, function(skill){
    SKILLS_DICT[skill[0]] = skill[1];
});

GET_SUBREGIONS_URL = "{{ get_subregions_url|safe }}";
