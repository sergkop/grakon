$(function(){
    $('form.uniForm').uniform();
});

function get_cookie(name){
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
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
