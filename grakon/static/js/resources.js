var Resource = {
    // Модель ресурса
    Model: Backbone.Model.extend({
        defaults: {
            value: 0,
            title: '',
            desc:  ''
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

    // View, отрисовывающий плашку ресурса
    View: Backbone.View.extend({
        initialize: function(){
            this.model = this.options.model;
            this.popup = this.options.popup;
            this.mode  = (this.options.mode === 'edit') ? 'edit' : 'new'
        },


        updateLayout: function() {
            $('.gr-resource-item', this.$el).text(this.model.get("title"));
            $('.gr-resource-item-desc', this.$el).text(this.model.get("desc"));
            if (this.mode === 'new') {
                this.$el.css({visibility: 'visible'});
                $(".gr-editing", this.$el).show(); // показываем кнопку редактирования
            }
        },

        renderEditWindow: function(){
            if (!PROFILE.username){
                login_dialog_init();
                return;
            }

            this.configurePopupWindow();
            this.popup.show();
        },

        configurePopupWindow: function() {
            var view = this,
                select = this.popup.children("select");

            Resource.helpers.clearPopupWindow(this.popup);

            // добавляем ресурсы в селектор
            if (select.children("option").length == 0){
                // если создаем ресурс, добавляем начальную строчку "Выбрать ресурс" в селектор
                if (this.mode === 'new') {
                    select.append($("<option/>").text("Выбрать ресурс").attr("value", ""))
                }

                _.each(RESOURCES, function(resource){
                    var selectItem = $("<option/>").text(resource[1]).attr("value", resource[0]);
                    select.append(selectItem);

                    // если есть редактируем ресурс, находим сразу выставляем его выбранным
                    if (this.mode === 'edit' && view.model.get("title").length > 0 && resource[1] == view.model.get("title")) {
                        selectItem.attr("selected", "selected")
                    }
                });
            }

            if (this.mode === 'edit') {
                // забиваем описание, если есть
                $("textarea", this.popup).val(this.model.get("desc"));

                // поправляем надписи в попапе в соответвствие с режимом
                $('.popup-action-label', this.popup).text('Изменить ресурс');
                $('#add_idea_resource_btn', this.popup).text('Изменить')
            } else {
                $('.popup-action-label', this.popup).text('Новый ресурс');
                $('#add_idea_resource_btn', this.popup).text('Добавить')
            }

            // цепляем правильный обработчик
            $("#add_idea_resource_btn", this.popup).click(function() {
                view.savePopupData()
            });

            // выставляем позицию попапа
            var dx = (this.$el.offset().left+this.$el.width()/2) - (this.popup.width()/2);
            var dy = this.$el.offset().top;
            this.popup.css("top", dy).css("left", dx);

        },

        /*
         * сохранение данных из окна-попапа
         */
        savePopupData: function(){

            this.model.set({
                value: $("select", this.popup).val(),
                title: $('select option:selected', this.popup).text(),
                desc:  $("textarea", this.popup).val()
            });

            this.popup.hide()
            this.updateLayout(); // cразу показываем на странице изменения, не дожидаясь аякса

            dialog_post_shortcut(
                ADD_RESOURCE_URL,
                {
                    "ct": this.popup.attr("ct"),
                    "id": this.popup.attr("entity"),
                    "resource": this.model.get("value"),
                    "description": this.model.get("desc"),
                    "provider": "true"
                },
                function(){}, // делаем офигительное ничего
                false
            )();
        }
    }),

    helpers: {
        clearPopupWindow: function(popupWindow) {
            $("select", popupWindow).html('');
            $("textarea", popupWindow).val('');
            $("#add_idea_resource_btn", popupWindow).unbind('click');
        }
    }
}

// Вешаем обработчики на кпонки ресурсов
$(function(){

    // Adding resources
    $(".add-resource-btn").click(function() {
        var cont = $(this).closest(".gr-ideas-item"),
            newItem = new Resource.Model(),
            itemsList = $(".resources-list", cont),
            lastItem = $(".resource-list-item", itemsList).last(),
            popup = $("#add_resource_popup"),
            newItemCont;

        // если последний элемент списка уже пустой, берем его как шаблон
        if ($(".gr-resource-item", lastItem).text().length == 0) {
            newItemCont = lastItem;
        } else {
            // иначе -- создаем новый
            lastItem.after(
                '<div class="resource-list-item" style="visibility: hidden;">' +
                    '<div class="gr-resource-item"></div>' +
                    '<i class="gr-editing edit-resource-item" style="display: none;">&nbsp;</i>' +
                    '<p class="gr-resource-item-desc"></p>' +
                '</div>');

            newItemCont = $(".resource-list-item", itemsList).last()
        }

        var view = new Resource.View({
                model: newItem,
                el: newItemCont,
                popup: popup,
                mode: 'new'
            });

        view.renderEditWindow();
    });


    // Editing resource item
    $(".edit-resource-item").live('click', function() {
        var itemCont = $(this).closest(".resource-list-item"),
            resource = new Resource.Model({
                title: $(".gr-resource-item", itemCont).text(),
                desc:  $(".gr-resource-item-desc", itemCont).text()
            });

        var popup = $("#add_resource_popup");

        var view = new Resource.View({
            model: resource,
            el: itemCont,
            popup: popup,
            mode: 'edit'
        });

        view.renderEditWindow();
    });

    // Resources list edit mode: on
    $(".edit-resource-list").click(function(){
        var elem = $(this),
            cont = elem.closest(".gr-ideas-item");  // контейнер со списком ресурсов
        $(".gr-editing", cont).show(); // показываем кнопки напротив элементов
        $(".action-btns", cont).show(); // показываем кнопки действий
        elem.hide(); // прячем кнопку общего редактирования
    });

    // Resources list edit mode: off
    $(".gr-ideas-item .cancel-res-editing-btn").click(function(){
        var cont = $(this).closest(".gr-ideas-item");
        $(".gr-editing", cont).hide(); // скрываем кнопки напротив элементов
        $(".action-btns", cont).hide(); // скрываем кнопки действий
        $("#resources_edit_btn", cont).show(); // показываем кнопку общего редактирования
        Resource.helpers.clearPopupWindow($("#add_resource_popup"));
    })
})
