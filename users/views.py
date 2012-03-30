# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
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
    profile_view = None # 'my_profile' or 'edit_profile'

    def get_profile(self):
        raise NotImplemented

    def get_context_data(self, **kwargs):
        ctx = super(BaseProfileView, self).get_context_data(**kwargs)
        profile = self.get_profile()

        ctx.update({
            'profile': profile,
            'profile_view': self.profile_view,
            'own_profile': profile==self.request.profile,
        })
        return ctx

class ProfileView(BaseProfileView, TemplateView):
    profile_view = 'my_profile'

    def get_profile(self):
        return get_object_or_404(Profile, username=self.kwargs.get('username'))

view_profile = ProfileView.as_view()

class MyProfileView(BaseProfileView, TemplateView):
    profile_view = 'my_profile'

    def get_profile(self):
        return self.request.profile

my_profile = login_required(MyProfileView.as_view())

class EditProfileView(BaseProfileView, UpdateView):
    form_class = ProfileForm
    profile_view = 'edit_profile'

    def get_profile(self):
        return self.request.profile

    def get_object(self):
        return self.request.profile

    def get_success_url(self):
        return reverse('my_profile')

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
