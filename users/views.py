# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

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
