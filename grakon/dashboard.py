# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from django import forms
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.utils.timezone import utc

from admin_tools.dashboard import modules, Dashboard
from qsstats import QuerySetStats

from services.models import Email
from tools.ideas.models import Idea
from tools.projects.models import Project
from tools.tasks.models import Task
from users.models import Message

class PeriodForm(forms.Form):
    start = forms.DateTimeField()
    end = forms.DateTimeField()
    mailtypes = forms.Select()

class SiteStats(modules.DashboardModule):
    title = u'Общая статистика'
    template = 'dashboard/stats.html'

    def init_with_context(self, context):
        if self._initialized:
            return

        request = context['request']

        # Date range
        if 'start' in request.GET and 'end' in request.GET:
            enddate = datetime.strptime(request.GET['end'], '%d.%m.%Y %X').replace(tzinfo=utc)
            startdate = datetime.strptime(request.GET['start'], '%d.%m.%Y %X').replace(tzinfo=utc)
        else:
            enddate = datetime.today().replace(tzinfo=utc)
            startdate = enddate - timedelta(days=30)

        # TODO: remove it
        qs = LogEntry.objects.filter(action_time__lte=enddate, action_time__gte=startdate)
        self.children = qs.select_related('content_type', 'user')[:10]

        self.mailtypes = Email.objects.distinct().values_list('type', flat=True)

        self.period_form = PeriodForm({'start': startdate, 'end': enddate,
                'mailtypes.choices': self.mailtypes})

        # E-mails
        self.mailtype = request.GET.get('mailtype', 'all')
        mails = Email.objects.all()
        if self.mailtype != 'all':
            mails = mails.filter(type=self.mailtype)
        mails_read = mails.filter(is_read=True)

        self.mails_qss = QuerySetStats(mails, 'time')
        self.mails_read_qss = QuerySetStats(mails_read, 'time')
        data = self.mails_qss.time_series(startdate, enddate)
        self.mail_values = [t[1] for t in data]

        # {model: (queryset, time_field)}
        querysets = {
            'users': (User.objects.filter(is_active=True), 'date_joined'),
            'ideas': (Idea.objects.all(), 'add_time'),
            'projects': (Project.objects.all(), 'add_time'),
            'tasks': (Task.objects.all(), 'add_time'),
            'messages': (Message.objects.all(), 'time'),
        }

        for model_type in querysets:
            qss = QuerySetStats(*querysets[model_type])
            setattr(self, model_type+'_qss', qss)
            data = qss.time_series(startdate, enddate)
            setattr(self, model_type+'_values', [d[1] for d in data])

            self.day_captions = [t[0].day for t in data]

        self._initialized = True

class CustomIndexDashboard(Dashboard):
    def __init__(self, **kwargs):
        Dashboard.__init__(self, **kwargs)
        self.children.append(modules.ModelList(title = u'Пользователи', models=('django.contrib.auth.*',)))

        self.children.append(modules.AppList(title=u'Приложения', exclude=('django.contrib.*',)))

        self.children.append(modules.AppList(title=u'Администрирование', models=('django.contrib.*',)))

        self.children.append(modules.Group(title=u"Статистика", display="tabs",
                children=[SiteStats(title=u'Общая статистика', limit=10)]))
