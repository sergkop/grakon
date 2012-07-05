var Resource = {

    /* View, отрисовывающий плашку ресурса */
    ItemView: Backbone.View.extend({
        initialize: function(){
            _.extend(this, _.pick(this.options, 'parent', 'provider'))
        },

        events: {
            "click .js-edit-resource": "renderEditWindow"
        },

        renderEditWindow: function() {
            // перед показом окна -- обновляем список уже назначенных ресурсов
            this.existingResources = this.parent.existingResources;

            //  отбивка для не аутентифицированных
            if (!PROFILE.username){
                login_dialog_init();
                return;
            }

            // координаты для попапа
            var position = {
                top: this.$el.offset().top,
                left: (this.$el.offset().left+this.$el.width()*1.5)
            };

            var popupView = new Resource.PopupView({
                ct: this.parent.ct,
                entity_id: this.parent.entity_id,
                mode: "edit",
                provider: this.provider,
                position: position,
                callback: this.updateLayout,
                removeCallback: this.remove,
                caller: this
            });

            popupView.show();
        },


        fetchFromHTML: function() {
            this.obj = {
                title:  $.trim(this.$el.text()),
                value: this.$el.attr("name"),
                descr:  this.$el.attr("descr")
            };

            this.parent.existingResources.push(this.$el.attr("name"));
        },

        updateLayout: function(obj) {

            this.obj = {
                value: obj.resource,
                title: obj.title,
                descr: obj.description
            };

            this.parent.existingResources.push(this.obj.value);

            this.render()
        },

        render: function() {
            $(".gr-resource-title", this.$el).text(this.obj.title);
            this.$el.attr("name", this.obj.value);

            if (this.obj.descr) {
                this.$el.addClass("gr-resource-item-active");
                this.$el.attr("descr", this.obj.descr);
            }
        },

        remove: function() {
            this.parent.existingResources = _.without(this.parent.existingResources, this.obj.value);
            this.$el.remove()
        }
    }),

    /** View, отвечающий за список ресурсов
     * Параметры:
     * @param el        Элемент списка на странице
     * @param addBtn    Элемент списка на странице
     * @param popupTpl  Строка-шаблон попап-окна
     * @param itemTpl   Строка-шаблон для создания новых элементов
     * @param [provider="true"] Необязательный флаг провайдера
     */
    ListView: Backbone.View.extend({
        initialize: function(){
            var view = this;

            _.extend(this, _.pick(this.options, 'provider', 'addBtn', 'itemTpl'));

            this.existingResources = [];
            this.getEntityParams(this.$el);

            // показ попапа для добавления ресурса
            this.addBtn.click( $.proxy( this.renderAddWindow, this ) );


            // для всех существующих ресурсов создаются вьюшки
            $(".gr-resource-item", this.$el).each(function() {
                new Resource.ItemView({
                    el: $(this),
                    parent: view,
                    provider: view.provider
                }).fetchFromHTML();
            })
        },

        /* находим content_type и entity_instance_id либо в аттрибутах списка,
         * либо в атрибутах контейнера списка */
        getEntityParams: function(elem) {
            var ct = elem.attr("ct"),
                entity_id = elem.attr("instance_id");

            if (ct && entity_id) {
                this.ct = ct;
                this.entity_id = entity_id
            } else {
                var cont = this.$el.closest("[ct][instance_id]"); // ближайший контейнер с обоими аттрибутами
                if (cont) {
                    this.getEntityParams(cont)
                } else {
                    console.log('ct & instance_id not found')
                }
            }
        },

        updateLayout: function(obj) {
            $(".gr-resource-item", this.$el).last().parent().append(this.itemTpl);

            var newItem = $(".gr-resource-item", this.$el).last();

            new Resource.ItemView({
                el: newItem,
                parent: this,
                provider: this.provider
            }).updateLayout(obj)
        },

        renderAddWindow: function(){
            //  отбивка для не аутентифицированных
            if (!PROFILE.username){
                login_dialog_init();
                return;
            }

            // координаты попапа
            var position = {
                top: this.addBtn.offset().top,
                left: (this.addBtn.offset().left+this.addBtn.width() + 22)
            };


            var popupView = new Resource.PopupView({
                ct: this.ct,
                entity_id: this.entity_id,
                provider: this.provider,
                mode: "new",
                position: position,
                callback: this.updateLayout,
                caller: this
            });

            popupView.show();
        }
    }),


    /* View, окна добавления / редактирования ресурса */
    PopupView: Backbone.View.extend({

        template:   '<div id="{{popup_id}}" class="gr-small-popup gr-add-popup">' +
                        '<span class="popup-action-label">{{actionLabel}}</span>' +
                        '<div class="gr-close">&nbsp;</div>' +
                        '<select class="gr-mb10 gr-mt10" style="width:100%">' +
                            '{{#options}}' +
                                '<option value="{{value}}" {{selected}}>{{title}}</option>' +
                            '{{/options}}' +
                        '</select>' +
                        '<textarea style="width:100%" maxlength="140" rows="4" placeholder="Описание (не более 140 символов)">' +
                            '{{descr}}' +
                        '</textarea>' +
                        '<div align="right" class="gr-mt5">' +
                            '{{#buttons}}' +
                                '&nbsp;<span class="{{class}} highlight">{{text}}</span>' +
                            '{{/buttons}}' +
                        '</div>' +
                    '</div>',

        initialize: function() {
            this.el = "add_resource_popup";

            $("#" + this.el).remove();

            this.params = {};
            // параметры для отправки на сервер
            _.extend(this.params, _.pick(this.options, 'ct', 'entity_id', 'provider'));
            // параметры окна
            _.extend(this, _.pick(this.options, 'mode', 'position', 'callback', 'removeCallback', 'caller'))

            this.createNew();
            this.setListeners();
        },

        setListeners: function() {
            $(".gr-close", this.$el).on("click", $.proxy(this.remove, this)); // закрыть окно

            // общение с сервером
            $(".add_resource_btn", this.$el).on("click", $.proxy(this.addResource, this));
            $(".edit_resource_btn", this.$el).on("click", $.proxy(this.updateResource, this));
            $(".remove_resource_btn", this.$el).on("click", $.proxy(this.removeResource, this));
        },

        createNew: function() {
            var context = {popup_id: this.el},
                options = this.fetchAllowedResources();

            if (this.mode === 'new') {
                options.unshift({title:"Выбрать ресурс", selected: "selected", value: ""});

                _.extend(context, {
                    actionLabel: "Новый ресурс",
                    buttons: [{ text: "Добавить", class: "add_resource_btn" }]
                })
            } else {
                // считаем что здесь режим редактирования и вызывала окно вьюшка отдельного ресурса
                options.unshift({title:this.caller.obj.title, selected: "selected", value: this.caller.obj.value});

                _.extend(context, {
                    actionLabel: "Изменить ресурс",
                    buttons: [
                        { text: "Изменить", class: "edit_resource_btn" },
                        { text: "Удалить", class: "remove_resource_btn" }
                    ],
                    descr: this.caller.obj.descr
                })
            }

            context.options = options;
            // создаем попап по шаблону
            $("body").append(Mustache.render(this.template, context));
            // ссылка для view
            this.$el = $("#" + this.el);
            this.condifgurePosition();
        },

        fetchAllowedResources: function() {
            var popup = this,
                data  = [];

            _.each(RESOURCES, function(item) {
                if (!_.include(popup.caller.existingResources, item[0])) {
                    data.push({title:item[1], value: item[0]})
                }
            });

            return data
        },

        /* Выставляем позицию попапа */
        condifgurePosition: function() {
            this.$el.css("top", this.position.top)
                        .css("left", this.position.left);
        },

        /* Сохранение ресурса с данными из окна-попапа */
        addResource: function(){
            this.sendResourceActionRequest(ADD_RESOURCE_URL, this.callback);
        },

        /* Обновление ресурса на выбранный из окна-попапа */
        updateResource: function(){
            var popup = this;

            this.params.old_resource = this.caller.obj.value;
            this.sendResourceActionRequest(UPDATE_RESOURCE_URL, this.callback);
        },

        /* Удаление ресурса */
        removeResource: function() {
            this.sendResourceActionRequest(REMOVE_RESOURCE_URL, this.removeCallback);
        },

        sendResourceActionRequest: function(url, callback) {
            var view = this,
                data = {
                    title: $("select option:selected", this.$el).text(),
                    resource: $("select", this.$el).val(),
                    description: $("textarea", this.$el).val()
                };

            _.extend(this.params, data);

            // api сервера требует id
            this.params.id = this.params.entity_id;
            delete this.params.entity_id;

            post_shortcut(
                    url,
                    this.params,
                    function() {
                        if (callback) {
                            callback.call(view.caller, view.params)
                        }
                    },
                    false
            )();

            this.remove()
        },

        remove: function() {
            this.$el.remove();
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