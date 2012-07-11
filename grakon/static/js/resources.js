var Resource = {

    /* Базовый View ресурса */
    ItemView: Backbone.View.extend({
        template: '',

        initialize: function(){
            _.extend(this, _.pick(this.options, 'parent', 'provider'));
            this.obj = {}
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

            var popupView = new this.parent.popupClass({
                ct: this.parent.ct,
                entity_id: this.parent.entity_id,
                mode: "edit",
                provider: this.provider,
                position: this.getPopupPosition(),
                callback: this.updateLayout,
                removeCallback: this.remove,
                caller: this
            });

            popupView.show();
        },

        updateObj: function(obj) {

            _.extend(this.obj, {
                value: obj.resource,
                title: obj.title,
                descr: obj.description
            });

            if (this.parent.existingResources.indexOf(this.obj.value) === -1) {
                this.parent.existingResources.push(this.obj.value)
            }
        },

        addNew: function(obj){
            this.updateObj(obj);

            this.parent.$el.append(Mustache.render(this.template, {resource: this.obj}));
            this.$el = $(this.parent.itemSel, this.parent.$el).last();

            $('.js-edit-resource', this.$el).last().click($.proxy( this.renderEditWindow, this ));

        },

        updateLayout: function(obj) {
            this.updateObj(obj);
            this.render()
        },

        remove: function() {
            this.parent.existingResources = _.without(this.parent.existingResources, this.obj.value);
            this.$el.remove()
        }
    }),


    /** View, отвечающий за список ресурсов
     * Параметры:
     * @param el        Элемент списка на странице
     * @param addBtn    Элемент кнопки добавления ресурсов на странице
     * @param itemSel   Селектор отдельного элемента ресурса
     * @param itemClass Класс для View отдельного ресурса в списке
     * @param popupClass Класс для View попап окна
     * @param [provider="true"] Необязательный флаг провайдера
     */
    ListView: Backbone.View.extend({
        initialize: function(){
            var view = this;

            _.extend(this, _.pick(this.options, 'provider', 'addBtn', 'itemSel', 'itemClass', 'popupClass'));

            this.existingResources = [];
            this.getEntityParams(this.$el);

            // показ попапа для добавления ресурса
            this.addBtn.click( $.proxy( this.renderAddWindow, this ) );

            // для всех существующих ресурсов создаются вьюшки
            $(this.itemSel, this.$el).each(function() {
                new view.itemClass({
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
                if (cont.length > 0) {
                    this.getEntityParams(cont)
                } else {
                    console.log('ct & instance_id not found')
                }
            }
        },

        updateLayout: function(obj) {
            new this.itemClass({
                parent: this,
                provider: this.provider
            }).addNew(obj)
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


            var popupView = new this.popupClass({
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


    /* Базовый View, всплывающего окна добавления / редактирования ресурса */
    PopupWindowView: Backbone.View.extend({

        template: '', // должно быть переопределено в потомках

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
            var context = {popup_id: this.el};

            if (this.mode === 'new') {
                _.extend(context, {
                    actionLabel: "Новый ресурс",
                    buttons: [{ text: "Добавить", class: "add_resource_btn" }]
                })
            } else {
                _.extend(context, {
                    actionLabel: "Изменить ресурс",
                    buttons: [
                        { text: "Изменить", class: "edit_resource_btn" },
                        { text: "Удалить", class: "remove_resource_btn" }
                    ],
                    descr: this.caller.obj.descr
                })
            }

            this.updateContext(context);

            // создаем попап по шаблону
            $("body").append(Mustache.render(this.template, context));
            // ссылка для view
            this.$el = $("#" + this.el);
            this.condifgurePosition();
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
                data = this.fetchFromHTML();

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

_.extend(Resource, {

     /* view ресурса в виде плашки с выпадающим описанием */
    LabelItemView: Resource.ItemView.extend({
        template: '<span class="gr-resource-item {{#resource.descr}}gr-resource-item-active{{/resource.descr}}" name="{{resource.value}}" descr="{{resource.descr}}">' +
                    '<span class="gr-resource-title">{{resource.title}}</span><i>&nbsp;</i>' +
                    '<b class="js-edit-resource">&nbsp;</b>' +
                  '</span>',

        getPopupPosition: function() {
            return {
                top: this.$el.offset().top,
                left: (this.$el.offset().left+this.$el.width()*1.5)
            }
        },

        fetchFromHTML: function() {
            this.obj = {
                title:  $.trim(this.$el.text()),
                value: this.$el.attr("name"),
                descr:  this.$el.attr("descr")
            };

            this.parent.existingResources.push(this.$el.attr("name"));
        },

        render: function() {
            $(".gr-resource-title", this.$el).text(this.obj.title);
            this.$el.attr("name", this.obj.value);

            if (this.obj.descr) {
                this.$el.addClass("gr-resource-item-active");
            } else {
                this.$el.removeClass("gr-resource-item-active");
            }

            this.$el.attr("descr", this.obj.descr)
        }
    }),

    /* view ресурса в виде блока */
    BlockItemView: Resource.ItemView.extend({
        template: '<div class="gr-resource-needs gr-resource-highlighted">' +
                    '<h3>{{resource.value}}</h3>' +
                    '<p>{{resource.descr}}</p>' +
                    '<div style="text-align: right;"><i class="gr-editing js-edit-resource">&nbsp;</i></div>' +
                  '</div>',

        getPopupPosition: function() {
            return {
                top: this.$el.offset().top,
                left: (this.$el.offset().left)
            }
        },

        fetchFromHTML: function() {
            this.obj = {
                title: $('h3', this.$el).text(),
                value: $('h3', this.$el).text(),
                descr: $('p', this.$el).text()
            };

            this.parent.existingResources.push(this.$el.attr("name"));
        },

        render: function() {
            $("h3", this.$el).text(this.obj.value);
            $("p", this.$el).text(this.obj.descr);
        }
    }),

    /* Класс всплывающего окна с selector'ом доступных ресурсов */
    PopupSelectorView: Resource.PopupWindowView.extend({

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

        updateContext: function(context) {
            var options = this.fetchAllowedResources();

            if (this.mode === "new") {
                options.unshift({title:"Выбрать ресурс", selected: "selected", value: ""});

            } else {
                // считаем что здесь режим редактирования и вызывала окно вьюшка отдельного ресурса
                options.unshift({title:this.caller.obj.title, selected: "selected", value: this.caller.obj.value});
            }

            context.options = options
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

        fetchFromHTML: function() {
            return {
                title: $("select option:selected", this.$el).text(),
                resource: $("select", this.$el).val(),
                description: $("textarea", this.$el).val()
            };
        }
    }),

    /* Класс всплывающего окна с input'ом для свободного добавления/редактирования ресурсов */
    PopupEditorView: Resource.PopupWindowView.extend({

        template:   '<div id="{{popup_id}}" class="gr-small-popup gr-add-popup">' +
                        '<span class="popup-action-label">{{actionLabel}}</span>' +
                        '<div class="gr-close">&nbsp;</div>' +
                        '<input type="text" placeholder="Название ресурса" class="gr-mb10 gr-mt10" style="width:100%" value="{{value}}"/>' +
                        '<textarea style="width:100%" maxlength="140" rows="4" placeholder="Описание (не более 140 символов)">' +
                            '{{descr}}' +
                        '</textarea>' +
                        '<div align="right" class="gr-mt5">' +
                            '{{#buttons}}' +
                                '&nbsp;<span class="{{class}} highlight">{{text}}</span>' +
                            '{{/buttons}}' +
                        '</div>' +
                    '</div>',

        updateContext: function(context) {
            if (this.mode === "edit") {
                context.value = this.caller.obj.value
            }
        },

        fetchFromHTML: function() {
            return {
                title: $("input", this.$el).val(),
                resource: $("input", this.$el).val(),
                description: $("textarea", this.$el).val()
            };
        }
    })
})

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