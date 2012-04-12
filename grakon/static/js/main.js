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

// Widget for choosing location path using several select elements
// Usage: (new SelectLocation({el: $(div), path: []})).render();
var SelectLocation = Backbone.View.extend({
    selectors: ['[name="region"]', '[name="district"]', '[name="location"]'],

    initialize: function(){
        var widget = this;
        widget.path = widget.options.path;

        widget.selects = [];
        widget.events = {};
        _.each(widget.selectors, function(selector, i){
            widget.selects.push(widget.$el.find(selector));
            widget.events["change "+selector] = function(){widget.select_change(i);};
        });
    },

    update_select_options: function(i, loc_id, selected){
        // loc_id is parent level loc_id, null for Russia regions. loc_id="" skips update
        // selected is selected option value (default is "")
        var select = this.selects[i];
        var widget = this;

        // Don't update select if parent's value is ""
        if (loc_id=="")
            return;

        if (loc_id==null)
            loc_id = "";

        // Update list of options
        $.getJSON(GET_SUBREGIONS_URL, {loc_id: loc_id}, function(data){
            select.children().remove();

            if (data.length>1){
                _.each(data, function(val){
                    select.append($("<option/>").val(val[0]).text(val[1]));
                });

                // Save select title from content to attribute
                select.children(":first").attr("empty-title", data[0][1]).text("");

                // Set selected option from path data
                select.val(selected);

                select.trigger("liszt:updated").parent().show();
            } else
                select.parent().hide();

            widget.update_empty_select(i);
        });
    },

    update_empty_select: function(i){
        var selects = this.selects;

        if (selects[i].val()==""){
            // Update select title when nothing is chosen
            var empty_title = selects[i].children(":first").attr("empty-title");
            $("#"+selects[i].attr("id")+"_chzn a.chzn-single span").html(empty_title);

            // Hide all selects on lower levels
            _.each(_.range(i+1, selects.length), function(j){
                selects[j].parent().hide();
            });
        }
    },

    render: function(){
        var widget = this;

        _.each(this.selects, function(select){
            // Run chosen initialization only once
            if (!select.hasClass("chzn-done"))
                select.chosen({
                    no_results_text: "Ни один вариант не соответствует",
                    allow_single_deselect: true
                });

            select.parent().hide();
        });

        // Set path values
        _.each(_.range(Math.min(widget.path.length+1, widget.selects.length)), function(i){
            var loc_id = (i>0) ? widget.path[i-1] : null; // null stands for country
            var selected = (i<widget.path.length) ? widget.path[i] : "";
            widget.update_select_options(i, loc_id, selected);
       });
    },

    select_change: function(i){
        // Attached to 'change' event of select
        var selects = this.selects;

        if (i+1<selects.length)
            this.update_select_options(i+1, selects[i].val(), "");

        // Hide all selects at deep levels
        _.each(_.range(i+2, selects.length), function(j){
            selects[j].parent().hide();
        });

        this.update_empty_select(i);
    }
});

// TODO: bug with styling of edit field
var TagsView = Backbone.View.extend({
    events: {
        "click .add-tag-btn": "edit",
        "click .edit-tag-btn": "edit",
        "click .save-tag-btn": "save"
    },

    initialize: function(){
        this.choices = this.options.choices;
        this.save_url = this.options.save_url;
        this.select = this.$el.find(".tag-edit select")
    },

    edit: function(){
        var el = this.$el;
        var select = this.select;

        el.children(".tag-view").hide();
        el.children(".tag-edit").show();

        select.children().remove();

        // Init select options
        _.each(this.choices, function(tag_data){
            select.append($("<option/>").attr("value", tag_data[0]).html(tag_data[1]));
        });

        // Mark selected options
        el.find("span[data-name]").each(function(i){
            select.children('option[value="'+$(this).attr("data-name")+'"]').attr("selected", "");
        });

        if (!select.hasClass("chzn-done"))
                select.chosen({
                    no_results_text: "Ни один вариант не соответствует"
                });
        select.trigger("liszt:updated");
    },

    save: function(){
        var el = this.$el;
        var select = el.find(".tag-edit select");

        el.children(".tag-view").show();
        el.children(".tag-edit").hide();

        el.find("span[data-name]").remove();

        if (select.val()){
            _.each(select.val().reverse(), function(resource, i){
                var title = RESOURCES_DICT[resource];
                if (i>0)
                    title += ", ";

                var span = $("<span/>").attr("data-name", resource).html(title);
                el.children(".tag-view").prepend(span);
            });

            $(".add-tag-btn").hide();
            $(".edit-tag-btn").show();
        } else {
            $(".add-tag-btn").show();
            $(".edit-tag-btn").hide();
        }
    },

    render: function(){}
});
