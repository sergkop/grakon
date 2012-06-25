$(function(){
    $.jTour({
        tourId:             'intro',
        onTourClose: function(){
                        window.document.location.href='/register';
        },
        pages:              [
            {url: '/', items: [
                {
                    sel:        '.gr-wrapper',
                    msg:        '<p align="center">Наша цель &mdash; помочь активным гражданам собрать ресурсы и&nbsp;идеи для&nbsp;решения общественных задач.</p>',
                    elemPos:    'cc',
                    boxPos:     'cc',
                    scrollTop:  -220,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.pause();
                    }
                }
            ]}, 
            {url: '/location/1/tasks', items: [
                {
                    sel:        '.gr-wrapper',
                    msg:        '<p>Основная структурная единица проекта&nbsp;&mdash; регион.</p><p>На&nbsp;его странице выводится вся существующая статистика: количество задач, проектов и&nbsp;участников.</p><p>Регион по&nbsp;умолчанию&nbsp;&mdash; Россия.</p>',
                    elemPos:    'cr',
                    boxPos:     'cr',
                    offsetLeft: -160,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.ym-column')
                            });
                            this.spotlight({
                                    element: $('.gr-content')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-wrapper',
                    msg:        '<p>Вы можете уточнить регион с&nbsp;помощью этого меню.</p>',
                    elemPos:    'tc',
                    boxPos:     'tc',
                    offsetTop:  80,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-breadcrumbs')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-wrapper',
                    msg:        '<p>Цитируя классиков: &laquo;Правильно поставленная задача &mdash; половина ее решения&raquo;.</p><p>Поэтому полезные дела на Граконе начинаются с постановки задач.</p>',
                    elemPos:    'cc',
                    boxPos:     'cc',
                    offsetTop:  -60,
                    offsetLeft: 320,
                    delay:      3000,
                    onStart:    function(e, b){
                             this.spotlight({
                                    element: $('.gr-ideas-list')
                            });
                            this.pause();
                    }
                }
            ]}, 
            {url: '/task/1', items: [
                {
                    sel:        '.gr-wrapper',
                    msg:        '<p>Задачей может быть любая проблема или инициатива, относящаяся к жизни граждан.</p>',
                    elemPos:    'cс',
                    boxPos:     'cс',
                    offsetTop:  -60,
                    offsetLeft: 320,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-wrapper')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-follow-button',
                    msg:        '<p>Для решения задач пользователи предлагают идеи.</p>',
                    elemPos:    'br',
                    boxPos:     'tr',
                    offsetTop:  10,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight();
                            this.spotlight({
                                    element: $('.gr-ideas-list')
                            });
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-ideas-list',
                    msg:        '<p>Популярность идеи оценивается по&nbsp;количеству предложенных пользователями ресурсов.</p><p>Любой пользователь может поддержать существующую идею ресурсом, заполнив форму слева.</p>',
                    elemPos:    'tc',
                    boxPos:     'tc',
                    offsetTop:  10,
                    offsetLeft: 60,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-add-icon:first')
                            });
                            jQuery('.gr-ideas-item:first').append('<div id="add_resource_popup" class="gr-small-popup gr-add-popup" style="display: block; top: 30px"><div class="gr-close js-close">&nbsp;</div><div class="ym-clearfix">&nbsp;</div><select class="gr-mb10 gr-mt10" style="width:100%"><option>Волонтер/Время</option></select><textarea style="width:100%" maxlength="140" rows="4" placeholder="Описание (не более 140 символов)"></textarea><div align="right" class="gr-mt5"><!--span class="highlighted">100</span--><span id="add_idea_resource_btn" class="highlight">Добавить</span></div></div>');
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-ideas-list',
                    msg:        '<p>По клику на счетчик ресурсов открывается более подробная информация о пользователях, поддержавших идею.</p>',
                    elemPos:    'tc',
                    boxPos:     'tc',
                    offsetTop:  70,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight({
                                    element: $('.gr-ideas-item:first .gr-slider:first')
                            });
                            this.pause();
                            jQuery('#add_resource_popup').hide();
                            jQuery('.gr-ideas-item:first .gr-slider:first').show().removeClass('gr-slider-inactive');
                            jQuery('.gr-ideas-item:first .gr-source-list-slider').show();
                    }
                },
                {
                    sel:        '.js-link-to-project:first',
                    msg:        '<p>Чтобы собрать полный &laquo;комплект&raquo; ресурсов и&nbsp;скоординировать реализацию идеи, создается проект.</p>',
                    elemPos:    'tr',
                    boxPos:     'tl',
                    offsetTop:  -20,
                    offsetLeft: 30,
                    delay:      1000,
                    onStart:    function(e, b){
                            this.spotlight();
                            this.pause();
                    }
                }
            ]},

            {url: '/project/1', items: [
                {
                    sel:        '.gr-descr',
                    msg:        '<p>Здесь автор описывает суть и&nbsp;план реализации проекта, определяет дедлайн,</p>',
                    elemPos:    'tr',
                    boxPos:     'tl',
                    offsetTop:  -33,
                    offsetLeft: 30,
                    delay:      3000,
                    onStart:    function(e, b){
                            this.spotlight();
                            this.pause();
                    }
                },
                {
                    sel:        '.gr-side-item',
                    msg:        '<p>перечисляет необходимые ресурсы.</p><p>Пользователи могут присоединиться к&nbsp;проекту, предложив какой-либо ресурс.</p>',
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
                    sel:        '.gr-wrapper',
                    msg:        '<p align="center"><big>Когда все ресурсы найдены, начинайте воплощать ваши идеи в&nbsp;жизнь!</big></p>',
                    elemPos:    'cc',
                    boxPos:     'cc',
                    offsetTop:  100,
                    delay:      3000
                }
            ]}
        ]
    });
});
