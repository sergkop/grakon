var Comment = {
    generateCommentItem: function(data){
        return $( Mustache.render("{{>comment_item}}", data, PARTIALS) );
    },

    ItemView: Backbone.View.extend({
        initialize: function(){
            // Can't be implemented using events since respond buttons from child comments must be ignored
            var respondBtn = this.$el.children(".gr-info-bar").children(".js-comment-response");
            respondBtn.click( $.proxy(this.respondToComment, this) );
        },

        respondToComment: function(){
            this.field = this.$el.children(".js-comments").children("table");

            if (!PROFILE.id){
                login_dialog_init();
                return;
            }

            if (this.field.length==0){
                var field = Comment.generateAddCommentField();
                this.$el.children(".js-comments").prepend(field);

                new Comment.AddCommentFieldView({el: field});
            } else
                this.field.toggle();
        }
    }),

    generateAddCommentField: function(){
        return $( Mustache.render("{{>comment_field}}", {}, PARTIALS) );
    },

    // Takes keep_on_submit option
    AddCommentFieldView: Backbone.View.extend({
        events: {"click .ym-button": "addComment"},

        initialize: function(){
            this.textarea = $("textarea", this.$el).autosize();

            this.entity_id = this.$el.parent().parent().attr("e_id");
            this.ct_id = this.$el.parent().parent().attr("ct");
        },

        addComment: function(){
            var comment = $.trim( this.textarea.val() );

            if (comment===""){
                alert("Пожалуйста введите комментарий");
                return;
            }

            // TODO: get id of new comment
            post_shortcut(ADD_COMMENT_URL, {
                    id: this.entity_id,
                    ct: this.ct_id,
                    parent: this.$el.parent().parent().attr("comment_id"),
                    comment: comment
                },
                $.proxy(this.showAddedComment, this)
            )();
        },

        showAddedComment: function(){
            var comment_item = Comment.generateCommentItem({
                comment: {
                    entity_id: this.entity_id,
                    ct_id: this.ct_id,
                    comment_id: "", // TODO: get it
                    comment: this.textarea.val(),
                    time: "" // TODO: get it
                },
                author: PROFILE
            });

            this.$el.after(comment_item);

            new Comment.ItemView({el: comment_item});

            if (!this.options.keep_on_submit)
                this.$el.remove();
            else
                this.textarea.val("");
        }
    }),

    generateCommentsList: function(comments_data, ct, entity_id){
        var data = {
            comments: comments_data,
            ct: ct,
            e_id: entity_id,
            PROFILE: PROFILE
        };
        return $( Mustache.render("{{>comments_list}}", data, PARTIALS) ); 
    },

    CommentListView: Backbone.View.extend({
        initialize: function(){
            $(".gr-comment", this.$el).each(function(){
                new Comment.ItemView({el: $(this)});
            });

            new Comment.AddCommentFieldView({
                el: this.$el.children(".js-comments").children(".gr-add-comment"),
                keep_on_submit: true
            });
        }
    })
};

// onclick event for comments counter in info bar
function show_comments(btn){
    btn.parent().parent().siblings(".js-comments").toggle();
    btn.toggleClass("gr-active-link");
}
