// TODO: move it to generated script with python code data
GET_SUBREGIONS_URL = "/get_subregions";

$(function(){
    $("form.uniForm").uniform();
});

function get_cookie(name){
    var cookieValue = null;
    if (document.cookie && document.cookie!="") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// TODO: use list to set buttons (?)
function create_dialog(id, width, height, title, cancel_btn_title, buttons){
    $(function(){
        if (cancel_btn_title)
            buttons[cancel_btn_title] = function(){$("#"+id).dialog("close");};

        $("#"+id)
                .removeClass("hidden")
                .dialog({autoOpen: false, width: width, height: height, modal: true,
                        title: title, buttons: buttons})
                .dialog("close");
    });
}

// Shortcut used to send post requests from dialogs.
// If post response is "ok", provided function is performed and dialog is closed.
// Otherwise alert with error message appears.
function dialog_post_shortcut(id, url, params, on_success){
    return function(){
        params["csrfmiddlewaretoken"] = get_cookie("csrftoken");
        $.post(url, params, function(data){
            if (data=="ok"){
                $("#"+id).dialog("close");
                on_success();
            } else
                alert(data);
        });
    }
}


var SelectLocation = Backbone.View.extend({
    events: {
        'click [name="region"]': "open",
    },

    initialize: function(){
        this.path = this.options.path;
        this.selects = [
            this.$el.find('[name="region"]'),
            this.$el.find('[name="district"]'),
            this.$el.find('[name="location"]')
        ];

        this.last_select = this.selects[Math.min(this.path.length, 2)];
    },

    render: function(){
        
        // Set nodes visibility
        var path = this.path;
        _.each(this.selects, function(select, i){
            // TODO: make sure it is ran only once
            select.chosen({no_results_text: "No results matched"});

            if (i < Math.min(path.length, 2))
                select.parent().show();
            else
                select.parent().hide();
        });

        

        if (path.length < 3){
            // Update list of options
            $.getJSON(GET_SUBREGIONS_URL, {loc_id: this.last_select.val()}, function(data){
                
            });

            // TODO: set selected option

            
        }
    },

    open: function(){
        
    }
});



/* ---- Methods for manipulations with location selectors ---- */
// path is a list of region ids (top to bottom level) with length from 0 to 3
function init_select_location(div_id, path){
    var select_1 = $('#'+div_id+' [name="region"]');
    var select_2 = $('#'+div_id+' [name="tik"]');
    var select_3 = $('#'+div_id+' [name="uik"]');

    select_1.unbind().change(function(){
        select_3.parent().hide();
        REGION_NAME = "";
        TIK_NAME = "";

        if (select_1.val()==""){
            select_2.hide();
            select_2.val("").change();
        } else {
            REGION_NAME = select_1.children('option[value="'+select_1.val()+'"]').text();
            $.getJSON(GET_SUB_REGIONS_URL, {location: select_1.val()}, function(data){
                if (data.length>0){
                    //select_2.children('[value!=""]').remove();
                    select_2.show();
                    select_2.children().remove();

                    var empty_2 = $("<option/>").val("");
                    if (select_1.children('[value="'+select_1.val()+'"]').text()=="Зарубежные территории")
                        var txt = "Выбрать страну";
                    else
                        var txt = "Выбрать район (ТИК)";
                    select_2.append(empty_2.text(txt));

                    $.each(data, function(index, value){
                        select_2.append($("<option/>").val(value["id"]).text(value["name"]));
                    });
                    select_2.val(path.length>1 ? path[1] : "").change();
                }
            });
        }
    });

    select_2.unbind().change(function(){
        TIK_NAME = "";
        if (select_2.val()=="")
            select_3.parent().hide();
        else {
            TIK_NAME = select_2.children('option[value="'+select_2.val()+'"]').text();
            $.getJSON(GET_SUB_REGIONS_URL, {location: select_2.val()}, function(data){
                if (data.length>0){
                    select_3.parent().show();
                    select_3.children('[value!=""]').remove();
                    $.each(data, function(index, value){
                        select_3.append($("<option/>").val(value["id"]).text("УИК № "+value["name"]));
                    });
                    select_3.val(path.length>2 ? path[2] : "");
                } else
                    select_3.parent().hide();
            });
        }
    });

    select_1.val(path.length>0 ? path[0] : select_1.val()).change();
    select_2.val(path.length>1 ? path[1] : "").change();
    select_3.val(path.length>2 ? path[2] : "");

    $(".find_uik_btn").click(function(){find_uik_dialog_init();});
}