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
                    /*post_shortcut(UPDATE_TEXT_FIELD_URL, {
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
                            post_shortcut(REMOVE_LOCATION_URL, {
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