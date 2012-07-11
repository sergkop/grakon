var Resource = window.Resource || {};

Resource.Form = {

    /* view ресурса в виде плашки с выпадающим описанием */
    FItemView: Resource.LabelItemView.extend({
        template: '<span class="gr-resource-item {{#resource.descr}}gr-resource-item-active{{/resource.descr}}" name="{{resource.value}}" descr="{{resource.descr}}">' +
                        '<span class="gr-resource-title">{{resource.title}}</span><i>&nbsp;</i>' +
                        '<b class="js-edit-resource">&nbsp;</b>' +
                        '<input type="hidden" name="resource__{{resource.index}}__resource" value="{{resource.value}}"/>' +
                        '<input type="hidden" name="resource__{{resource.index}}__description" value="{{resource.descr}}"/>' +
                   '</span>',


        updateObj: function(obj) {
            var index = this.parent.existingResources.indexOf(obj.resource);

            if (index === -1) {
                this.parent.existingResources.push(obj.resource)
            }

            _.extend(this.obj, {
                value: obj.resource,
                title: obj.title,
                descr: obj.description,
                index: this.parent.existingResources.indexOf(obj.resource)
            });

        },

        render: function() {
            $(".gr-resource-title", this.$el).text(this.obj.title);
            this.$el.attr("name", this.obj.value);
            this.$el.attr("descr", this.obj.descr);

            $('input[type=hidden][name$="__resource"]', this.$el).attr("value", this.obj.value);
            $('input[type=hidden][name$="__description"]', this.$el).attr("value", this.obj.descr);


            if (this.obj.descr) {
                this.$el.addClass("gr-resource-item-active");
            } else {
                this.$el.removeClass("gr-resource-item-active");
            }
        }
    }),

    /* Класс всплывающего окна с input'ом для свободного добавления/редактирования ресурсов */
    FPopupEditorView: Resource.PopupEditorView.extend({

        sendResourceActionRequest: function(url, callback) {
            var data = this.fetchFromHTML();

            _.extend(this.params, data);

            if (callback) {
                callback.call(this.caller, this.params)
            }

            this.remove()
        }
    })
}