var RESOURCES = {{ resources|safe }};

var RESOURCES_DICT = {};
_.each(RESOURCES, function(resource){
    RESOURCES_DICT[resource[0]] = resource[1];
});

var GET_SUBREGIONS_URL = "{% url get_subregions %}";
var REMOVE_LOCATION_URL = "{% url remove_location %}";
var UPDATE_TEXT_FIELD_URL = "{% url update_text_field %}";

var ADD_RESOURCE_URL = "{% url add_resource %}";
var UPDATE_RESOURCE_URL = "{% url update_resource %}";
var REMOVE_RESOURCE_URL = "{% url remove_resource %}";

var ADD_COMMENT_URL = "{% url add_comment %}";

// TODO: use values from settings.py
// TODO: hide textarea while widget is loading
function create_tinymce_widget(textarea_id){
    tinyMCE.init({
        "elements": textarea_id,
        "width": "100%",
        "height": 300,

        "relative_urls": false,
        "theme_advanced_toolbar_location": "top",
        "theme_advanced_toolbar_align": "left",
        "language": "ru",
        "theme_advanced_buttons1": "bold,italic,underline,|,bullist,numlist,|,link,unlink,",
        "theme_advanced_buttons3": "",
        "theme_advanced_buttons2": "",
        "theme": "advanced",
        "strict_loading_mode": 1,
        "directionality": "ltr",
        "mode": "exact",

        "plugins": "autoresize",
        "autoresize_min_height": 300,
        "autoresize_max_height": 500
    });
}

function tinymce_editor(textarea_id){
    if (typeof tinyMCE === "undefined"){
        {% if TINYMCE_COMPRESSOR %}
            $.getScript("{% url tinymce-compressor %}", function(){
                tinyMCE_GZ.init({"themes": "advanced", "languages": "ru", "debug": false, "diskcache": true, "plugins": ""});
                create_tinymce_widget(textarea_id);
            });
        {% else %}
            $.getScript("{{ TINYMCE_JS_URL }}", function(){create_tinymce_widget(textarea_id);});
        {% endif %}
    } else
        create_tinymce_widget(textarea_id);
}

var PARTIALS = {{ mustache_partials|safe }};
