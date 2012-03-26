# -*- coding:utf-8 -*-
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from auth.forms import LoginForm, RegistrationForm
from auth.models import ActivationProfile
from auth.utils import authenticated_redirect

@authenticated_redirect('edit_profile')
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            # TODO: crashes on registering user with the same username
            user = form.save()
            return redirect('registration_completed')
    else:
        form = RegistrationForm()

    return TemplateResponse(request, 'auth/register.html', {'form': form})

@authenticated_redirect('my_profile')
def activate(request, activation_key):
    account = ActivationProfile.objects.activate_user(activation_key)
    if account:
        return redirect('activation_completed')
    return TemplateResponse(request, 'auth/activation_fail.html')

# TODO: introduce shortcut for it or write it shorter
@authenticated_redirect('my_profile')
def registration_completed(request):
    return TemplateResponse(request, 'auth/registration_completed.html')

@authenticated_redirect('my_profile')
def email_not_sent(request):
    return TemplateResponse(request, 'auth/email_not_sent.html')

@authenticated_redirect('my_profile')
def activation_completed(request):
    return TemplateResponse(request, 'auth/activation_completed.html')

# TODO: fix it
def password_change(request, **kwargs):
    if request.profile.is_loginza_user():
        return redirect('password_change_forbidden')
    return auth_views.password_change(request, **kwargs)

@authenticated_redirect('my_profile')
def login(request):
    return auth_views.login(request, 'auth/login.html', 'next', LoginForm)

def logout(request):
    next_page = reverse('main') if 'next' in request.REQUEST else None
    return auth_views.logout(request, next_page)

@authenticated_redirect('my_profile')
def password_reset_done(request):
    return TemplateResponse(request, 'auth/password_reset_done.html')

def password_change_done(request):
    return TemplateResponse(request, 'auth/password_change_done.html')
