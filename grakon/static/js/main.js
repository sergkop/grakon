$(function(){
    //$("form.uniForm").uniform();
    //$(".gr-side-item h4 i, .gr-login-info a").tipsy({gravity: 'n', opacity: .8});

    $("input[placeholder], textarea[placeholder]").placeholder();

    $("textarea").autosize();

    /* Для того, что бы ресайз выполнялся и при добавлении комментариев второго уровня */
    //$('body').bind('click',function(){$("textarea").autosize();});

    // Show/hide resources provided for idea
    $(".js-resources-list").click(function(){
        var slider = $(this).parent().parent();
        slider.toggleClass("gr-slider-inactive");
        slider.children(".gr-source-list-slider").slideToggle(100);
    });

    // Show/hide projects related to idea
    $(".js-projects").click(function(){
        $(this).parent().parent().parent().children(".js-projects-content").toggle();
        $(this).toggleClass("gr-active-link");
    });

    // TODO: move it to function and call explicitly
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

    // Closing popups
    $(".js-close").click(function(){
        $(this).parent().hide();
        return false;
    });

    $(".js-open-add-resource-button").click(function(){
        $("#add_project_resource_popup").show();
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
function post_shortcut(url, params, on_success, reload_page, form_id){
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
    input.attr("data-placeholder", " "); //Выбрать навыки и ресурсы
    if (!input.hasClass("chzn-done"))
        input.chosen();
    input.trigger("liszt:updated");
}

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

                    post_shortcut(editor.post_url, editor.post_params(value), function(){
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

function add_project_resource(ct, instance_id){
    post_shortcut(ADD_RESOURCE_URL, {
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
    post_shortcut(REMOVE_RESOURCE_URL, {
        "ct": ct,
        "id": instance_id,
        "resource": resource
    }, function(){
        $("#add_project_resource_popup").hide();
    }, true)();
}
