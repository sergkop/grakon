$(function(){
    var tourArr = {
        tourId:             'intro',
        onTourClose: function(){
                if(!PROFILE.username) {
                       window.document.location.href='/register?utm_campaign=tour&utm_medium=link&utm_source=main_page';  
                }
                else{
                         window.document.location.href='/location/1/tasks';  
                }
        },
        pages:              [
            {url: '/', items: [
                {
                    sel:        '.gr-wrapper',
                    msg:        '<p align="center">Наша цель &mdash; помочь активным гражданам собрать ресурсы и&nbsp;идеи для&nbsp;решения общественных задач.</p>',
                    elemPos:    'cc',
                    boxPos:     'cc',
                    offsetTop:  -220,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.pause();
                    }
                }
            ]}, 
            {url: '/location/1/tasks', items: [
                {
                    sel:        '.ym-column .ym-wrapper:first',
                    msg:        '<p>Основная структурная единица проекта&nbsp;&mdash; регион.</p><p>На&nbsp;его странице выводится вся существующая статистика: количество задач, проектов и&nbsp;участников.</p><p>Регион по&nbsp;умолчанию&nbsp;&mdash; Россия.</p>',
                    elemPos:    'bc',
                    boxPos:     'tc',
                    offsetTop:  30,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.ym-column .ym-wrapper:first')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-breadcrumbs',
                    msg:        '<p>Вы можете уточнить регион с&nbsp;помощью этого меню.</p>',
                    elemPos:    'bc',
                    boxPos:     'tc',
                    offsetTop:  10,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-breadcrumbs')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-follow-button',
                    msg:        '<p>Цитируя классиков: &laquo;Правильно поставленная задача &mdash; половина ее решения&raquo;.</p><p>Поэтому полезные дела на Граконе начинаются с постановки задач.</p>',
                    elemPos:    'tl',
                    boxPos:     'tl',
                    offsetTop:  0,
                    offsetLeft: -30,
                    delay:      3000,
                    onStart:    function(e, b){
                             this.spotlight({
                                    element: $('.gr-ideas-list')
                            });
                            this.pause();
                    }
                },
                {
                        sel:        '.gr-follow-button',
                        msg:        '<p>Рассмотрим пример задачи.</p><p>Перейти на нее можно, нажав на название.</p>',
                        elemPos:    'tl',
                        boxPos:     'tl',
                        offsetTop:  0,
                        offsetLeft: -30,
                        delay:      3000,
                        onStart:    function(e, b){
                                this.spotlight({
                                        element: $('.gr-ideas-item:first')
                                });
                                this.pause();
                        }
                    }
            ]}, 
            {url: '/task/1', items: [
                {
                    sel:        '.gr-ideas-list',
                    msg:        '<p>Задачей может быть любая общественная проблема или инициатива.</p>',
                    elemPos:    'tс',
                    boxPos:     'tc',
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-descr')
                            });
                            this.spotlight({
                                    element: $('h1')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-ideas-list',
                    msg:        '<p>Для решения задач пользователи предлагают идеи.</p>',
                    elemPos:    'tc',
                    boxPos:     'tc',
                    offsetTop:  -157,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight();
                            this.spotlight({
                                    element: $('#tour-content')
                            });
                            this.spotlight({
                                    element: $('.gr-add-icon')
                            });
                            this.pause();
                            $('.gr-add-popup').hide();
                            
                    }
                },
                {
                    sel:        '.gr-ideas-list',
                    msg:        '<p>Популярность идеи оценивается по&nbsp;количеству ресурсов, предложенных пользователями для ее реализации.</p><p>Любой участник может поддержать добавленную идею ресурсом, нажав на плюс напротив идеи и заполнив простую форму слева.</p>',
                    elemPos:    'tc',
                    boxPos:     'tc',
                    offsetTop:  10,
                    offsetLeft: 60,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-add-icon:first')
                            });
                           $('.gr-ideas-item:first').append('<div id="add_resource_popup" class="gr-small-popup gr-add-popup" style="display: block; top: 30px"><div class="gr-close js-close">&nbsp;</div><div class="ym-clearfix">&nbsp;</div><select class="gr-mb10 gr-mt10" style="width:100%"><option>Волонтер/Время</option></select><textarea style="width:100%" maxlength="140" rows="4" placeholder="Описание (не более 140 символов)"></textarea><div align="right" class="gr-mt5"><!--span class="highlighted">100</span--><span id="add_idea_resource_btn" class="highlight">Добавить</span></div></div>');
                            this.pause();
                            $('.gr-ideas-item:first .gr-slider:first').show().addClass('gr-slider-inactive');
                            $('.gr-ideas-item:first .gr-source-list-slider').hide();
                    }
                },
                {
                    sel:        '.gr-ideas-item:first h3',
                    msg:        '<p>По клику на счетчик ресурсов открывается более подробная информация о пользователях, поддержавших идею.</p>',
                    elemPos:    'bc',
                    boxPos:     'bc',
                    offsetTop:  150,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-ideas-item:first .gr-slider:first')
                            });
                            this.pause();
                            $('.gr-add-popup').hide();
                            $('.gr-ideas-item:first .gr-slider:first').show().removeClass('gr-slider-inactive');
                            $('.gr-ideas-item:first .gr-source-list-slider').show();
                    }
                },
                {
                    sel:        '.gr-descr',
                    msg:        '<p>Вернемся на страницу региона</p>',
                    elemPos:    'tc',
                    boxPos:     'tc',
                    delay:      3000
                }
                
            ]},
            {url: '/location/1/projects', items: [
                {
                    sel:        '.gr-follow-button',
                    msg:        '<p>Когда приходит время претворять идеи в&nbsp;жизнь, создается проект.</p><p>Список всех проектов региона можно посмотреть на соответствующей вкладке.</p><p>Рассмотрим подробнее страницу проекта.</p>',
                    elemPos:    'tl',
                    boxPos:     'tl',
                    offsetTop:  70,
                    offsetLeft: -30,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-ideas-list')
                            });
                            this.spotlight({
                                    element: $('.ym-column:first .ym-wrapper')
                            });
                            this.spotlight({
                                    element: $('.gr-follow-button')
                            });
                            this.pause();
                    }
                }
            ]},

            {url: '/project/1', items: [
                {
                    sel:        '.gr-descr',
                    msg:        '<p>Здесь автор описывает суть и&nbsp;план реализации проекта, определяет дедлайн...</p>',
                    elemPos:    'tr',
                    boxPos:     'tl',
                    offsetLeft: 20,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight();
                            this.spotlight({
                                    element: $('.ym-column:first .ym-wrapper')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-side-item',
                    msg:        '<p>перечисляет необходимые ресурсы.</p><p>Пользователи могут присоединиться к&nbsp;проекту, предложив один из них.</p><p>Для этого достаточно нажать на прямоугольник ресурса и добавить краткое пояснение.</p>',
                    elemPos:    'tr',
                    boxPos:     'tr',
                    offsetTop:  -25,
                    offsetLeft: -300,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight();
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-descr',
                    msg:        '<p align="center"><big>Когда вся команда собрана и ресурсы найдены, начинайте воплощать ваши идеи в&nbsp;жизнь!</big></p>',
                    elemPos:    'tc',
                    boxPos:     'tc',
                    delay:      3000
                }
            ]}
        ]
    }

    if (PROFILE.username)
        tourArr['pages'].splice(0, 1);

     $.jTour(tourArr);

});
