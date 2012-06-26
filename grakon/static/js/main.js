$(function(){
    //$("form.uniForm").uniform();
    //$(".gr-side-item h4 i, .gr-login-info a").tipsy({gravity: 'n', opacity: .8});

    $("input[placeholder], textarea[placeholder]").placeholder();

    // Show/hide resources provided for idea
    $(".js-resources-list").click(function(){
        var slider = $(this).parent().parent();
        slider.toggleClass("gr-slider-inactive");
        slider.children(".gr-source-list-slider").slideToggle(100);
    });

    // Show/hide popups with descriptions of idea resources
    $(".gr-resource-item-active")
            .hover(function(){
                var label = $(this);
                var resource_popup = $(".gr-hover-popup");
                resource_popup.children("div").text(label.attr("descr"));
                var dx = (label.offset().left+label.width()/2) - (resource_popup.width()/2);
                var dy = label.offset().top + label.height() + 10;
                resource_popup.css("top", dy).css("left", dx).show();
            })
            .mouseleave(function(){$(".gr-hover-popup").hide();});

    // Show/hide projects related to idea
    $(".js-projects").click(function(){
        $(this).parent().parent().children(".js-projects-content").toggle();
        $(this).toggleClass("gr-active-link");
    });

    // Show/hide followers of the task
    $(".js-follow").click(function(){
        $(this).parents().children(".js-follow-content").toggle();
        $(this).toggleClass("gr-active-link");
    });

    $(".js-slide-close").click(function(){
        $(this).parent().hide();
        $(this).parent().parent().children(".gr-info-bar").children().removeClass("gr-active-link");
    });

    // Slide-down profile menu
    $(".gr-login-user").click(function(){
        $(".gr-login-user-sub").toggle();
    });

    // Hide list of idea resources
    $(".js-close-inactive").click(function(){
        var slider = $(this).parent();
        slider.children(".gr-small-popup").hide();
        slider.addClass("gr-slider-inactive");
        slider.children(".gr-source-list-slider").hide();

        // TODO: is it correct?
        $(".js-resource-items span").removeClass("gr-resource-item-active");
    });

    // Adding resources to idea
    $(".js-add").click(function(){
        if (!PROFILE.username){
            login_dialog_init();
            return;
        }

        var button = $(this);
        var idea = button.parent().parent().parent().parent();

        var resource_popup = $("#add_resource_popup");

        var select = resource_popup.children("select");
        if (select.children("option").length == 0){
            select.append($("<option/>").text("Выбрать ресурс").attr("value", ""));
            _.each(RESOURCES, function(resource){
                select.append($("<option/>").text(resource[1]).attr("value", resource[0]));
            });
        }

        var dx = (button.offset().left+button.width()/2) - (resource_popup.width()/2);
        var dy = button.offset().top + button.height() + 10;
        resource_popup.css("top", dy).css("left", dx).show();

        resource_popup.show();

        //$(".gr-hover-popup").hide();
        //$(".js-resource-items span").removeClass("gr-resource-item-active");

        $("#add_idea_resource_btn").click(function(){
            var resource = resource_popup.children("select").val();

            if (resource == ""){
                alert("Необходимо выбрать ресурс");
                return;
            }

            // TODO: don't reload page
            dialog_post_shortcut(ADD_RESOURCE_URL, {
                "ct": idea.attr("ct"),
                "id": idea.attr("instance_id"),
                "provider": "true",
                "resource": resource,
                "description": resource_popup.children("textarea").val()
            }, function(){
                $("#add_resource_popup").hide();
            }, true)();
        });
    });

    // Closing popups
    $(".js-close").click(function(){
        $(this).parent().hide();
        return false;
    });

    $(".js-open-add-resource-button").click(function(){
        $("#add_project_resource_popup").show();
    });

    // Remove resource from idea
    $(".js-remove-resource").click(function(){
        var idea = $(this).parent().parent().parent().parent().parent().parent();
        var label = $(this).parent();

        dialog_post_shortcut(REMOVE_RESOURCE_URL, {
            "ct": idea.attr("ct"),
            "id": idea.attr("instance_id"),
            "resource": label.attr("name"),
            "provider": "true"
        }, function(){
            label.remove();
            $(".gr-small-popup").hide();
            alert("Ваш ресурс удален");
        }, true)();
    });

    // Default tipsy settings
    $.fn.tipsy.defaults.delayIn = 150;
    $.fn.tipsy.defaults.delayOut = 200;
    $.fn.tipsy.defaults.fade = true;
    $.fn.tipsy.defaults.opacity = 0.6;
});

function get_cookie(name){
    var cookie_value = null;
    if (document.cookie && document.cookie!="") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + "=")) {
                cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookie_value;
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

// TODO: what if response is not successful?
// Shortcut used to send post requests from dialogs.
// If post response is "ok", provided function is performed and dialog is closed.
// Otherwise alert with error message appears.
// If form_id is specified, params is updated with form data.
function dialog_post_shortcut(url, params, on_success, reload_page, form_id){
    return function(){
        params["csrfmiddlewaretoken"] = get_cookie("csrftoken");
        if (form_id){
            // TODO: this may not work with complex form fields
            _.each($("#"+form_id).serializeArray(), function(field){
                params[field.name] = field.value;
            });
        }
        $.post(url, params, function(data){
            if (data=="ok"){
                on_success();
                if (reload_page)
                    window.location.reload();
            } else
                alert(data);
        });
    }
}

function login_dialog_init(){
    $("#login_dialog").dialog("open");
    $('#login_form [name="csrfmiddlewaretoken"]').val(get_cookie("csrftoken"));
}

function select_resources(input){
    input.attr("data-placeholder", "Выберите навыки и ресурсы");
    if (!input.hasClass("chzn-done"))
        input.chosen();
    input.trigger("liszt:updated");
}

// Widget for choosing location path using several select elements
// Usage: (new SelectLocation({el: $(div), path: []})).render()
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

var ResourcesEditor = Backbone.View.extend({
    initialize: function(){
        this.$el;
    },

    add_item: function(resource, descr){
        
    }
});

// TODO: add "add location" button and save
// Widget for inline editing of the list of locations
// Usage: new LocationEditor({el: $(div), edit_btn: $(edit_btn), ct: ct_id, entity_id: entity_id})
var LocationEditor = Backbone.View.extend({
    initialize: function(){
        this.edit_btn = this.options.edit_btn;
        var editor = this;

        editor.edit_btn.click(function(){editor.edit();});
    },

    edit: function(){
        var editor = this;
        editor.edit_btn.hide();

        editor.$el.addClass("gr-editor");

        // Add cancel and save buttons
        //var cancel_btn = $("<span/>").text("Отмена")
        //        .addClass("gr-editor-btn")
        //        .click(function(){editor.recover();});
        //editor.$el.after(cancel_btn);

        //var add_location_btn = $("<span/>").text("Добавить территорию")
        //        .addClass("gr-editor-btn")
        //        .click(function(){
        //            // TODO: implement it
        //        });

        var save_btn = $("<span/>").text("Сохранить")
                .addClass("gr-editor-btn")
                .click(function(){
                    editor.recover();
                    /*dialog_post_shortcut(UPDATE_TEXT_FIELD_URL, {
                        ct: editor.options.ct,
                        id: editor.options.entity_id,
                        field: editor.options.field,
                        value: value
                    }, function(){
                        editor.old_value = value;
                        editor.recover();
                    })();*/
                });
        editor.$el.after(save_btn);

        editor.$el.children("li").each(function(index){
            var li = $(this);

            $("<span/>")
                    .attr("title", "Отказаться от участия")
                    .addClass("remove-li-btn gr-close")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        li.css("background-color", "#D9BDFF");

                        var confirmation = confirm("Вы действительно хотите отказаться от участия в этом районе?");
                        li.css("background-color", "#FFFFFF");

                        // TODO: use model dialog here?
                        if (confirmation)
                            dialog_post_shortcut(REMOVE_LOCATION_URL, {
                                "loc_id": li.attr("loc_id"),
                                "ct": editor.options.ct,
                                "id": editor.options.entity_id
                            }, function(){li.remove();})();
                    })
                    .prependTo(li);
        });
    },

    recover: function(){
        this.edit_btn.show();
        this.$el.removeClass("gr-editor");
        this.$el.next().remove();
        this.$el.next().remove();

        this.$el.children("li").each(function(index){
            $(this).children(":first").remove();
        });
    }
});

function prevent_enter_in_form(selector){
    $(selector).keydown(function(event){
        if(event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });
}

// TODO: take max_length into account (for text type)
// TODO: visual bug when there is no text (for text type)
// TODO: set focus on editing element
// TODO: on save use text/html filtered on server? (for security)
// Widget for inline editing of text fields
// Usage: new TextFieldEditor({el: $(div), edit_btn: $(edit_btn), add_btn: $(add_btn),
//            ct: ct_id, entity_id: entity_id, field: field, type: "text" or "html"})
// Also takes optional post_url and post_params parameters
var TextFieldEditor = Backbone.View.extend({
    initialize: function(){
        this.edit_btn = this.options.edit_btn;
        this.add_btn = this.options.add_btn;

        var editor = this;
        this.edit_btn.click(function(){editor.edit();});
        this.add_btn.click(function(){editor.edit();});

        this.post_url = this.options.post_url || UPDATE_TEXT_FIELD_URL;
    },

    post_params: function(value){
        if (this.options.post_params)
            return this.options.post_params(this, value);

        return {
            ct: this.options.ct,
            id: this.options.entity_id,
            field: this.options.field,
            value: value
        };
    },

    edit: function(){
        var editor = this;

        editor.edit_btn.hide();
        editor.add_btn.hide();

        // Add cancel and save buttons
        var cancel_btn = $("<span/>").text("Отмена")
                .addClass("gr-editor-btn")
                .click(function(){editor.recover();});
        editor.$el.after(cancel_btn);

        var save_btn = $("<span/>").text("Сохранить")
                .addClass("gr-editor-btn")
                .click(function(){
                    if (editor.options.type == "text")
                        var value = editor.$el.text();
                    else
                        // TODO: take related editor, not active
                        var value = tinyMCE.activeEditor.getContent();

                    dialog_post_shortcut(editor.post_url, editor.post_params(value), function(){
                        editor.old_value = value;
                        editor.recover();
                    })();
                });
        editor.$el.after(save_btn);

        // Create editor widget
        if (editor.options.type == "text"){
            editor.old_value = editor.$el.text();
            editor.$el.attr("contenteditable", "true").addClass("gr-editor");
        } else {
            editor.$el.hide();
            editor.old_value = editor.$el.html();

            editor.textarea = $("<textarea/>")
                    .attr("id", "id_"+editor.options.field)
                    .html(editor.old_value);
            editor.$el.after(editor.textarea);

            tinymce_editor("id_"+editor.options.field);
        }
    },

    // Hide editor widget and show updated content
    recover: function(){
        this.edit_btn.show();
        this.$el.next().remove();
        this.$el.next().remove();
        if (this.options.type == "text"){
            this.$el.removeAttr("contenteditable").removeClass("gr-editor").text(this.old_value);
        } else {
            this.$el.html(this.old_value).show();
            this.$el.next().remove();
            this.$el.next().remove();
        }
        if (this.old_value == "")
            this.add_btn.show();
    }
});

function load_disqus(id, url, category){
    if (typeof DISQUS === "undefined"){
        disqus_identifier = id;
        disqus_url = url;
        disqus_category_id = category;

        $.getScript("http://"+disqus_shortname+".disqus.com/embed.js");
    } else
        DISQUS.reset({
            reload: true,
            config: function () {
                this.page.identifier = id;  
                this.page.url = url;
                this.page.category = category;
            }
        });
}

// TODO: use backbone view and hide comments on second click
function show_comments(btn, id, url, category){
    if ($("#disqus_thread").length > 0){
        $("#disqus_thread").remove();
        return;
    }

    var disqus_div = $("<div/>").attr("id", "disqus_thread")
            .css("background-color", "#D8E6ED").css("padding", "1em");
    btn.parent().after(disqus_div);

    load_disqus(id, url, category);
}

function add_project_resource(ct, instance_id){
    dialog_post_shortcut(ADD_RESOURCE_URL, {
        "ct": ct,
        "id": instance_id,
        "resource": $("#add_project_resource_popup input").val(),
        "description": $("#add_project_resource_popup textarea").val()
    }, function(){
        $("#add_project_resource_popup").hide();
    }, true)();
}

// TODO: popup with confirmation before deletion
function remove_project_resource(ct, instance_id, resource){
    dialog_post_shortcut(REMOVE_RESOURCE_URL, {
        "ct": ct,
        "id": instance_id,
        "resource": resource
    }, function(){
        $("#add_project_resource_popup").hide();
    }, true)();
}
