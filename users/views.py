# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
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

    def get_context_data(self, **kwargs):
        ctx = super(BaseProfileView, self).get_context_data(**kwargs)
        profile = self.profile = get_object_or_404(Profile, username=self.kwargs.get('username'))

        own_profile = (profile==self.request.profile)

        tabs = [
            ('view', u'Профиль', profile.get_absolute_url(), 'profiles/view.html', ''),
        ]

        if own_profile:
            tabs.append(('edit', u'Редактировать', reverse('edit_profile', args=[profile.username]),
                    'profiles/edit.html', ''))

        self.info = profile.info()

        ctx.update({
            'tab': self.tab,
            'tabs': tabs,
            'profile': profile,
            'own_profile': own_profile,
            'info': self.info,
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

def update_resources(request):
    if not (request.is_ajax() and request.user.is_authenticated()):
        return HttpResponse(u'Вам необходимо войти в систему')

    request.profile.update_resources(request.POST.getlist('value[]', None))
    return HttpResponse('ok')
