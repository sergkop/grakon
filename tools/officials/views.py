# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.participants.models import EntityParticipant
from elements.utils import table_data
from elements.views import entity_base_view, participants_view
from services.disqus import disqus_page_params
from tools.officials.forms import OfficialForm
from tools.officials.models import Official

class BaseOfficialView(object):
    template_name = 'officials/base.html'
    tab = None

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseOfficialView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))
        self.participants_url = reverse('official_participants', args=[id])
        ctx.update(entity_base_view(self, Official, id))

        tabs = [
            ('view', u'Информация', self.entity.get_absolute_url(), 'officials/view.html', ''),
            ('wall', u'Обсуждение', reverse('official_wall', args=[id]), 'disqus/comments.html', 'wall-tab'),
            ('participants', u'Участники', self.participants_url, 'elements/table_tab.html', ''),
        ]

        if ctx['is_admin']:
            tabs.append(('edit', u'Редактировать', reverse('edit_official', args=[id]),
                    'elements/edit_form.html', ''))

        ctx.update({
            'tabs': tabs,
            'official': self.entity,
            'follow_button': {
                'cancel_msg': u'Вы хотите отписаться от новостей об этом чиновнике?',
                'cancel_btn': u'Отписаться',
                'cancel_btn_long': u'Отписаться',
                'confirm_msg': u'Вы хотите следить за новостями об этом чиновнике?',
                'confirm_btn': u'Следить',
                'confirm_btn_long': u'Следить',
            },
        })
        ctx.update(disqus_page_params('official/'+str(id),
                reverse('official_wall', args=[id]), 'officials'))
        return ctx

class OfficialView(BaseOfficialView, TemplateView):
    tab = 'view'

    def update_context(self):
        return table_data(self.request, 'posts', self.entity.get_posts, 5)

class OfficialWallView(BaseOfficialView, TemplateView):
    tab = 'wall'

class OfficialParticipantsView(BaseOfficialView, TemplateView):
    tab = 'participants'

    def update_context(self):
        return participants_view(self)

# TODO: test that only admin can edit official page
class EditOfficialView(BaseOfficialView, UpdateView):
    form_class = OfficialForm
    tab = 'edit'

    def get_object(self):
        return get_object_or_404(Official, id=int(self.kwargs.get('id')))

    def get_success_url(self):
        return reverse('official', args=[self.kwargs.get('id')])

# TODO: need more strict condition
edit_official = login_required(EditOfficialView.as_view())

class CreateOfficialView(CreateView):
    template_name = 'officials/create.html'
    form_class = OfficialForm
    model = Official

    def form_valid(self, form):
        official = form.save()

        EntityParticipant.objects.add(official, self.request.profile, 'admin')
        EntityParticipant.objects.add(official, self.request.profile, 'follower')

        response = super(CreateOfficialView, self).form_valid(form)
        return response

create_official = login_required(CreateOfficialView.as_view())
