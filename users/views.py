# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from grakon.context_processors import project_settings
from services.email import send_email
from users.forms import ProfileForm
from users.models import Profile

class BaseProfileView(object):
    template_name = 'profiles/base.html'
    tab = None # 'view' or 'edit'

    def update_context(self):
        return {}

    def get_profile(self):
        return get_object_or_404(Profile, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        ctx = super(BaseProfileView, self).get_context_data(**kwargs)
        self.profile = self.get_profile()

        own_profile = (self.profile==self.request.profile)

        # TODO: take edit url using urlresolvers
        tabs = [
            ('view', u'Профиль', self.profile.get_absolute_url(), 'profiles/view.html', ''),
        ]

        if own_profile:
            tabs.append(('edit', u'Редактировать',
                    reverse('edit_profile', kwargs={'username': self.profile.username}),
                    'profiles/edit.html', ''))

        ctx.update({
            'profile': self.profile,
            'tab': self.tab,
            'tabs': tabs,
            'own_profile': own_profile,
            'info': self.profile.get_related_info(),

            'resources': [{'name': r.resource, 'title': r.get_resource_display()}
                    for r in self.profile.get_related_info()['resources']],
        })
        ctx.update(self.update_context())
        return ctx

class ProfileView(BaseProfileView, TemplateView):
    tab = 'view'

view_profile = ProfileView.as_view()

# TODO: test that only user can edit his own profile
class EditProfileView(BaseProfileView, UpdateView):
    form_class = ProfileForm
    tab = 'edit'

    def get_object(self):
        return self.request.profile

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.profile.username})

edit_profile = login_required(EditProfileView.as_view())

def remove_account(request):
    if request.user.is_authenticated():
        subject = u'[УДАЛЕНИЕ АККАУНТА] %s - %s %s' % (request.user.username,
                request.profile.first_name, request.profile.last_name)

        context = project_settings(request)
        context.update({'profile': request.profile})
        html = render_to_string('letters/remove_account.html', context)

        send_email(subject, settings.ADMIN_EMAIL, html)
    return TemplateResponse(u'Чтобы удалить аккаунт, необходимо войти в систему')

@login_required
def profile(request):
    """ Redirects user to profile page after logging in (used to overcome django limitation) """
    return redirect(request.profile.get_absolute_url())
