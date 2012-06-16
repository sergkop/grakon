from admin_tools.dashboard import modules
#from admin_tools.utils import AppListElementMixin, uniquify
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django import forms

from datetime import datetime

class PeriodForm(forms.Form):
    start = forms.DateTimeField()
    end = forms.DateTimeField()

class AllRecentActions(modules.RecentActions):
    title = _('Recent Actions')
    template = 'dashboard/recent_actions.html'
    limit = 10
    include_list = None
    exclude_list = None
    
    filter_title = _("Select period for report")
    start_title = _("Start")
    end_title= _("End")
    submit_title = _("Apply")
    periodForm = PeriodForm({"start":datetime.now(),"end":datetime.now()})

    def init_with_context(self, context):
        if self._initialized:
            return
        from django.db.models import Q
        from django.contrib.admin.models import LogEntry

        request = context['request']
        def get_qset(list):
            qset = None
            for contenttype in list:
                if isinstance(contenttype, ContentType):
                    current_qset = Q(content_type__id=contenttype.id)
                else:
                    try:
                        app_label, model = contenttype.split('.')
                    except:
                        raise ValueError('Invalid contenttype: "%s"' % contenttype)
                    current_qset = Q(
                        content_type__app_label=app_label,
                        content_type__model=model
                    )
                if qset is None:
                    qset = current_qset
                else:
                    qset = qset | current_qset
            return qset
        

        if len(request.GET)>0 and request.GET["start"] and request.GET["end"]:
            qs = LogEntry.objects.filter(action_time__lte=datetime.strptime(request.GET["end"],'%d.%m.%Y %X'), action_time__gte=datetime.strptime(request.GET["start"], '%d.%m.%Y %X'))
        else:
            qs = LogEntry.objects.all()

        if self.include_list:
            qs = qs.filter(get_qset(self.include_list))
        if self.exclude_list:
            qs = qs.exclude(get_qset(self.exclude_list))

        self.children = qs.select_related('content_type', 'user')[:self.limit]

        if not len(self.children):
            self.pre_content = _('No recent actions.')
        self._initialized = True


