# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elements.admins.models import EntityAdmin
from elements.followers.models import EntityFollower
from elements.utils import table_data
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
        self.official = get_object_or_404(Official, id=int(self.kwargs.get('official_id')))

        is_admin = False
        is_follower = False
        if self.request.user.is_authenticated():
            is_admin = EntityAdmin.objects.is_admin(self.official, self.request.profile)
            is_follower = EntityFollower.objects.is_followed(self.official, self.request.profile)

        self.participants_url = reverse('official_participants', args=[self.official.id])

        tabs = [
            ('view', u'Информация', self.official.get_absolute_url(), 'officials/view.html', ''),
            ('wall', u'Обсуждение', reverse('official_wall', args=[self.official.id]), 'officials/wall.html', 'wall-tab'),
            ('participants', u'Участники', self.participants_url, 'officials/participants.html', ''),
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
            'admins_title': u'Админы',
            'participants_url': self.participants_url,
        })
        ctx.update(self.update_context())
        ctx.update(disqus_page_params('official/'+str(self.official.id),
                reverse('official_wall', args=[self.official.id]), 'officials'))
        return ctx

class OfficialView(BaseOfficialView, TemplateView):
    tab = 'view'

    def update_context(self):
        return table_data(self.request, 'posts', self.official.get_posts, 5)

class OfficialWallView(BaseOfficialView, TemplateView):
    tab = 'wall'

class OfficialParticipantsView(BaseOfficialView, TemplateView):
    tab = 'participants'

    # TODO: this method should be moved to utils
    def update_context(self):
        participants_types = [
            ('admins', u'Админы', 'officials/admins.html', self.official.get_admins),
            ('followers', u'Следят', 'officials/followers.html', self.official.get_followers),
        ]

        p_type = self.request.GET.get('type', '')
        if p_type not in map(lambda p: p[0], participants_types):
            p_type = 'admins'

        name, title, template, method = filter(lambda p: p[0]==p_type, participants_types)[0]

        ctx = table_data(self.request, 'participants', method)
        ctx.update({
            'table_cap_choices': map(lambda p: (self.participants_url+'?type='+p[0], p[1]), participants_types),
            'table_cap_title': title,
            'table_cap_template': template,
        })
        return ctx

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
    template_name = 'officials/create.html'
    form_class = OfficialForm
    model = Official

    def form_valid(self, form):
        official = form.save()

        EntityAdmin.objects.add(official, self.request.profile)
        EntityFollower.objects.add(official, self.request.profile)

        response = super(CreateOfficialView, self).form_valid(form)
        return response

create_official = login_required(CreateOfficialView.as_view())
