# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from tools.officials.forms import OfficialForm
from tools.officials.models import Official

class BaseOfficialView(object):
    template_name = 'officials/base.html'
    tab = None # 'view' or 'edit'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseOfficialView, self).get_context_data(**kwargs)
        official = self.official = get_object_or_404(Official, id=self.kwargs.get('official_id'))

        is_admin = (profile==self.request.profile)

        tabs = [
            ('view', u'Информация', profile.get_absolute_url(), 'officials/view.html', ''),
        ]

        if own_profile:
            tabs.append(('edit', u'Редактировать', reverse('edit_profile', args=[profile.username]),
                    'profiles/edit.html', ''))

        self.info = official.info()

        ctx.update({
            'tab': self.tab,
            'tabs': tabs,
            'info': self.info,
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

    #def get_object(self):
    #    return self.request.profile

    def get_success_url(self):
        return reverse('official', args=[])

# TODO: need more strict condition
edit_official = login_required(EditOfficialView.as_view())
