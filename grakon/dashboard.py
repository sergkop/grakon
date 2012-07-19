# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from django import forms
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.utils.timezone import utc

from admin_tools.dashboard import modules, Dashboard
from qsstats import QuerySetStats

from elements.widgets import DateTimeWidget
from services.models import Email
from tools.ideas.models import Idea
from tools.projects.models import Project
from tools.tasks.models import Task
from users.models import Message

dt_format = '%d/%m/%Y %H:%M'

class PeriodForm(forms.Form):
    start = forms.DateTimeField(input_formats=[dt_format], widget=DateTimeWidget(format=dt_format, attrs={'size': 15}))
    end = forms.DateTimeField(input_formats=[dt_format], widget=DateTimeWidget(format=dt_format, attrs={'size': 15}))

class BaseSiteStats(modules.DashboardModule):
    def get_time_range(self, request):
        # Date range
        if 'start' in request.GET and 'end' in request.GET:
            self.enddate = datetime.strptime(request.GET['end'], dt_format).replace(tzinfo=utc)
            self.startdate = datetime.strptime(request.GET['start'], dt_format).replace(tzinfo=utc)
        else:
            self.enddate = datetime.now().replace(tzinfo=utc)
            self.startdate = self.enddate - timedelta(days=30)

        self.children = [1] # TODO: hack to make tab shown

    def get_models_data(self, querysets):
        """ querysets = {model: (queryset, time_field)} """
        for model_type, (queryset, time_field) in querysets.iteritems():
            qss = QuerySetStats(queryset, time_field)

            data = qss.time_series(self.startdate, self.enddate)

            counts = [d[1] for d in data]
            qss.last_week = sum(counts[-7:])
            qss.last_month = sum(counts[-30:])

            self.day_captions = [t[0].day for t in data]

            setattr(self, model_type+'_qss', qss)
            setattr(self, model_type+'_values', counts)

class ContentStats(BaseSiteStats):
    title = u'Контент'
    template = 'dashboard/stats.html'

    def init_with_context(self, context):
        self.get_time_range(context['request'])

        self.period_form = PeriodForm({'start': self.startdate, 'end': self.enddate})

        self.get_models_data({
            'users': (User.objects.filter(is_active=True), 'date_joined'),
            'ideas': (Idea.objects.all(), 'add_time'),
            'projects': (Project.objects.all(), 'add_time'),
            'tasks': (Task.objects.all(), 'add_time'),
            'messages': (Message.objects.all(), 'time'),
        })

class EmailStats(BaseSiteStats):
    title = u'Emails'
    template = 'dashboard/emails.html'

    def init_with_context(self, context):
        self.children = [1] # TODO: hack to make tab shown

        self.mailtypes = Email.objects.distinct().values_list('type', flat=True)

        # TODO: choose time range from the first email till the last
        # TODO: show average read time and rate (for each 24h slot and total)
        # TODO: get analytics from GA

        #self.period_form = PeriodForm({'start': self.startdate, 'end': self.enddate,
        #        'mailtypes.choices': self.mailtypes})

        # E-mails
        self.mailtype = context['request'].GET.get('mailtype', 'all')
        emails = Email.objects.all()
        if self.mailtype != 'all':
            emails = emails.filter(type=self.mailtype)

        first_time = emails.order_by('time')[0].time
        last_time = emails.order_by('-time')[0].time

        self.enddate = datetime.now().replace(tzinfo=utc)
        self.startdate = self.enddate - timedelta(days=30)

        self.get_models_data({
            'emails': (emails, 'time'),
            'emails_read': (emails.filter(is_read=True), 'time'),
        })

        self.all_emails_values = [
            self.emails_read_values,
            [self.emails_values[i]-self.emails_read_values[i] for i in range(len(self.emails_values))],
        ]

class StatsDashboard(Dashboard):
    def __init__(self, **kwargs):
        Dashboard.__init__(self, **kwargs)

        tech_models_list = (
            'djcelery.*',
            'authentication.*',
            'notifications.*',
            'social_auth.*',
            'services.*',
        )

        exclude=('django.contrib.sites.*', 'django.contrib.auth.models.Group')

        self.children = [
            modules.AppList(title=u'Контент', exclude=tech_models_list+exclude),

            modules.AppList(title=u'Приложения', models=tech_models_list, exclude=exclude),

            modules.Group(title=u'Статистика', display='tabs', children=[
                ContentStats(),
                EmailStats(),
            ]),
        ]
