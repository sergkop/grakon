var Resource = {
    // Модель ресурса
    Model: Backbone.Model.extend({
        defaults: {
            value: "",
            title: "",
            desc:  ""
        },

        initialize: function() {
            // ошибки валидации пока валим в консоль
            this.bind("error", function(model, error) {
                console.log( "Error: " + error )
            })
        },

        // на клиенте валидируются длина описания и наличие id ресурса
        validate: function(attributes) {
            if ( attributes.desc && attributes.desc.length > 140 ) {
                return "Описание ресурса должно быть короче 140 символов"
            }

            // если id = 0, или не число
            if (+( attributes.value )){
                return "Не верный id ресурса"
            }
        }
    }),

    /*
     * View, отрисовывающий плашку ресурса
     */
    ItemView: Backbone.View.extend({
        initialize: function(){
            this.model = this.options.model;
            this.parent = this.options.parent;

        },

        events: {
            "click .js-remove-resource": "renderEditWindow"
        },

        renderEditWindow: function() {
            var
                popup = $("#add_resource_popup"),
                position;

            //  отбивка для не аутентифицированных
            if (!PROFILE.username){
                login_dialog_init();
                return;
            }

            position = {
                top: this.$el.offset().top,
                left: (this.$el.offset().left+this.$el.width()*1.5)
            };

            var popupView = new Resource.PopupView({
                el: popup,
                ct: this.parent.ct,
                entity_id: this.parent.entity_id,
                mode: "edit",
                provider: this.options.provider,
                callback: this.updateLayout,
                removeCallback: this.remove,
                caller: this
            });

            popupView.configure(this.model, position);
            popupView.show();
        },


        fetchFromHTML: function() {
            this.model.set({
                title:  $.trim(this.$el.text()),
                value: this.$el.attr("name"),
                desc:  this.$el.attr("descr")
            })
        },

        updateLayout: function(obj) {

            this.model.set({
                value: obj.resource,
                title: obj.title,
                desc:  obj.description
            });

            this.render()
        },

        render: function() {
            this.$el.prepend(this.model.get("title"));
            this.$el.attr("name", this.model.get("value"));

            if (this.model.get("desc")) {
                this.$el.addClass("gr-resource-item-active");
                this.$el.attr("descr", this.model.get("desc"));
            }
        },

        remove: function() {
            this.$el.remove();
            $("br + br", this.parent.$el).remove()
        }
    }),


    /*
     *View, отвечающий за список ресурсов
     */
    ListView: Backbone.View.extend({
        initialize: function(){
            var view = this;

            this.template = this.options.template;
            this.getEntityParams();

            this.options.addBtn.click(function(){
                view.renderAddWindow();
            });

            $(".gr-resource-item", this.$el).each(function() {

                new Resource.ItemView({
                    el: $(this),
                    model: new Resource.Model(),
                    parent: view,
                    provider: view.options.provider
                }).fetchFromHTML();
            })

        },


        events: {
        //    "click .add-resource-btn": "renderAddWindow"
        },

        /*
         * находим content_type и entity_instance_id либо в аттрибутах списка, либо в атрибутах
         * контейнера списка
         */
        getEntityParams: function() {
            this.ct = this.$el.attr("ct");
            this.entity_id = this.$el.attr("instance_id");

            if (!this.ct || !this.entity_id) {
                var cont = this.$el.closest("[ct][instance_id]");
                this.ct = cont.attr("ct");
                this.entity_id = cont.attr("instance_id");
            }

        },

        updateLayout: function(obj) {

            $(".gr-resource-item", this.$el).last().parent().append(this.template);

            var newItem = $(".gr-resource-item", this.$el).last();

            new Resource.ItemView({
                el: newItem,
                model: new Resource.Model(),
                parent: this
            }).updateLayout(obj)
        },

        renderAddWindow: function(){
            var elem = this.options.addBtn,
                newItem = new Resource.Model(),
                popup = $("#add_resource_popup"),
                position, ct, entity_id;

            //  отбивка для не аутентифицированных
            if (!PROFILE.username){
                login_dialog_init();
                return;
            }

            position = {
                top: elem.offset().top,
                left: (elem.offset().left+elem.width()/2) - (popup.width()/2)
            };



            var popupView = new Resource.PopupView({
                el: popup,
                ct: this.ct,
                entity_id: this.entity_id,
                provider: this.options.provider,
                mode: "new",
                callback: this.updateLayout,
                caller: this
            });

            popupView.configure(newItem, position);
            popupView.show();
        }
    }),


    /*
     *View, окна добавления / редактирования ресурса
     */
    PopupView: Backbone.View.extend({

        initialize: function() {

            this.params = {
                "ct": this.options.ct,
                "id": this.options.entity_id
            };

            if (this.options.provider) {
                this.params.provider = this.options.provider
            }

            this.mode  = (this.options.mode === "edit") ? "edit" : "new"
            this.callback = this.options.callback;
            this.caller   = this.options.caller;
            this.clearPopupWindow();

            $(".add_resource_btn", this.$el).on("click", $.proxy(this.savePopupData, this));
            //$(".edit_resource_btn", this.$el).on("click", $.proxy(this.savePopupData, this));
            $(".remove_resource_btn", this.$el).on("click", $.proxy(this.removeResource, this));

        },

        events: {
        },

        configure: function(resource, position) {


            this.configureForm(resource);

            this.configureLabels();

            this.condifgurePosition(position);
        },


        /*
         * заполняем селектор
         */
        configureForm: function(resource) {
            var view = this,
                select = this.$el.children("select");



            // добавляем ресурсы в селектор
            if (select.children("option").length == 0){
                // если создаем ресурс, добавляем начальную строчку "Выбрать ресурс" в селектор
                if (this.mode === "new") {
                    select.append($("<option/>").text("Выбрать ресурс").attr("value", ""))
                } else {
                    // при редактировании забиваем описание, если есть
                    $("textarea", this.$el).val(resource.get("desc"));
                }

                _.each(RESOURCES, function(resource_item){
                    var selectItem = $("<option/>").text(resource_item[1]).attr("value", resource_item[0]);
                    select.append(selectItem);

                    // если есть редактируем ресурс, находим сразу выставляем его выбранным
                    if (view.mode === "edit" && resource.get("title").length > 0 && resource_item[1] === resource.get("title")) {
                        selectItem.attr("selected", "selected")
                    }
                });
            }
        },

        /*
         * оформление окна
         */
        configureLabels: function() {
            if (this.mode === "edit") {
                // поправляем надписи в попапе в соответвствие с режимом
                $(".popup-action-label", this.$el).text("Изменить ресурс");

                // оставляем видимыми лишь нужные кнопки
                $(".add_resource_btn", this.$el).hide();
      //          $(".edit_resource_btn", this.$el).show();
                $(".remove_resource_btn", this.$el).show()
            } else {

                $(".popup-action-label", this.$el).text("Новый ресурс");

                // оставляем видимыми лишь нужные кнопки
                $(".add_resource_btn", this.$el).show();
                $(".edit_resource_btn", this.$el).hide();
                $(".remove_resource_btn", this.$el).hide()
            }

        },


        /*
         * выставляем позицию попапа
         */
        condifgurePosition: function(position) {
            this.$el.css("top", position.top)
                        .css("left", position.left);
        },


        /*
         * очистка окна-попапа
         */
        clearPopupWindow: function() {
            $("select", this.$el).html("");
            $("textarea", this.$el).val("");
            // FIXME: надо просто пересоздавать попап каждый раз с шаблона
            $(".add_resource_btn", this.$el).off("click");
            $(".edit_resource_btn", this.$el).off("click");
            $(".remove_resource_btn", this.$el).off("click");
        },


        /*
         * сохранение данных из окна-попапа
         */
        savePopupData: function(){
            this.sendResourceActionRequest(ADD_RESOURCE_URL, this.callback);
        },

        /*
         * удаление данных из окна-попапа
         */
        removeResource: function() {
            this.sendResourceActionRequest(REMOVE_RESOURCE_URL, this.options.removeCallback);
        },


        sendResourceActionRequest: function(url, callback) {
            var view = this;

            this.params.title       = $("select option:selected", this.$el).text();
            this.params.resource    = $("select", this.$el).val();
            this.params.description = $("textarea", this.$el).val();

            this.$el.hide();

            dialog_post_shortcut(
                    url,
                    this.params,
                    function() {
                        if (callback) {
                            callback.call(view.caller, view.params)
                        }
                    },
                    false
            )();
        },

        show: function() {
            this.$el.show();
        }
    })
}

$(function() {
    // Show/hide popups with descriptions of idea resources
    $(".gr-resource-item-active")
            .live("hover", function(){
                var label = $(this);
                var resource_popup = $(".gr-hover-popup");
                resource_popup.children("div").text(label.attr("descr"));
                var dx = (label.offset().left+label.width()/2) - (resource_popup.width()/2);
                var dy = label.offset().top + label.height() + 10;
                resource_popup.css("top", dy).css("left", dx).show();
            })
            .live("mouseleave", function(){$(".gr-hover-popup").hide()});
})