# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.models import EntityAdmin, EntityFollower
from tools.officials.forms import OfficialForm
from tools.officials.models import Official

class BaseOfficialView(object):
    template_name = 'officials/base.html'
    tab = None # 'view' or 'edit'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseOfficialView, self).get_context_data(**kwargs)
        self.official = get_object_or_404(Official, id=int(self.kwargs.get('official_id')))

        is_admin = False
        is_follower = False
        if self.request.user.is_authenticated():
            is_admin = EntityAdmin.objects.is_admin(self.official, self.request.profile)
            is_follower = EntityFollower.objects.is_followed(self.official, self.request.profile)

        tabs = [
            ('view', u'Информация', self.official.get_absolute_url(), 'officials/view.html', ''),
        ]

        if is_admin:
            tabs.append(('edit', u'Редактировать', reverse('edit_official', args=[self.official.id]),
                    'officials/edit.html', ''))

        self.info = self.official.info()

        ctx.update({
            'tools_menu_item': True,
            'tab': self.tab,
            'tabs': tabs,
            'info': self.info,
            'official': self.official,
            'is_follower': is_follower,
            'is_admin': is_admin,
        })
        ctx.update(self.update_context())
        return ctx

class OfficialView(BaseOfficialView, TemplateView):
    tab = 'view'

view_official = OfficialView.as_view()

# TODO: test that only admin can edit official page
class EditOfficialView(BaseOfficialView, UpdateView):
    form_class = OfficialForm
    tab = 'edit'

    def get_object(self):
        return get_object_or_404(Official, id=int(self.kwargs.get('official_id')))

    def get_success_url(self):
        return reverse('official', args=[self.kwargs.get('official_id')])

# TODO: need more strict condition
edit_official = login_required(EditOfficialView.as_view())


class CreateOfficialView(CreateView):
    template_name = 'violations/create.html'
    form_class = ViolationForm
    model = Violation

    def form_valid(self, form):
        violation = form.save(commit=False)
        violation.source = self.request.profile
        violation.save()

        response = super(ReportViolationView, self).form_valid(form)
        return response
