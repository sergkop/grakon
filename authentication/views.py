# -*- coding:utf-8 -*-
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from authentication.forms import LoginForm, RegistrationForm, SocialRegistrationForm
from authentication.models import ActivationProfile
from authentication.utils import authenticated_profile_redirect

@authenticated_profile_redirect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            profile = form.save()
            return redirect('registration_completed')
    else:
        form = RegistrationForm()

    return TemplateResponse(request, 'auth/register.html', {'form': form})

def social_registration_pipeline(request, *args, **kwargs):
    # TODO: don't show this form if kwargs['user']
    if kwargs['user']:
        return None
    return redirect('social_registration')

# TODO: @authenticated_profile_redirect ?
def social_registration(request):
    # TODO: if user is logged in - redirect

    from social_auth.utils import setting
    name = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
    data = request.session.get(name)

    if not data:
        return redirect('login')

    details = data['kwargs']['details']

    # TODO: data from google
    #data['kwargs']['response']['link']
    #data['kwargs']['response']['picture']
    #data['kwargs']['response']['verified_email']

    # TODO: data['kwargs']['is_new'] - what is it?

    email_verified = False
    if data['backend']=='google-oauth2' and data['kwargs']['response']['verified_email']:
        email_verified = True

    form_params = {'email_verified': email_verified}
    if email_verified:
        form_params['email'] = details['email']

    if request.method == 'POST':
        form = SocialRegistrationForm(request.POST, **form_params)

        if form.is_valid():
            profile = form.save()

            if email_verified:
                from django.conf import settings
                name = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
                data[name] = 5 # TODO: fix it; start with settings.SOCIAL_AUTH_PIPELINE_RESUME_ENTRY
                data['kwargs']['user'] = profile.user
                data['kwargs']['is_new'] = True
                request.session[name] = data

                return redirect('socialauth_complete', backend=data['backend'])

            # TODO: if email needs to be confirmed, redirect to registration_completed or /complete/<backend>/,
            #       else - profile
            return redirect('registration_completed')
    else:
        form = SocialRegistrationForm(**form_params)

    form.initial['first_name'] = details['first_name']
    form.initial['last_name'] = details['last_name']
    form.initial['username'] = details['username']

    if not email_verified:
        form.initial['email'] = details['email']

    return TemplateResponse(request, 'auth/register.html', {'form': form})

@authenticated_profile_redirect
def activate(request, activation_key):
    account = ActivationProfile.objects.activate_user(activation_key)
    if account:
        return redirect('activation_completed')
    return TemplateResponse(request, 'auth/activation_fail.html')

# TODO: introduce shortcut for it or write it shorter
@authenticated_profile_redirect
def registration_completed(request):
    return TemplateResponse(request, 'auth/registration_completed.html')

@authenticated_profile_redirect
def email_not_sent(request):
    return TemplateResponse(request, 'auth/email_not_sent.html')

@authenticated_profile_redirect
def activation_completed(request):
    return TemplateResponse(request, 'auth/activation_completed.html')

# TODO: fix it
def password_change(request, **kwargs):
    if request.profile.is_loginza_user():
        return redirect('password_change_forbidden')
    return auth_views.password_change(request, **kwargs)

@authenticated_profile_redirect
def login(request):
    return auth_views.login(request, 'auth/login.html', 'next', LoginForm)

def logout(request):
    next_page = reverse('main') if 'next' in request.REQUEST else None
    return auth_views.logout(request, next_page)

@authenticated_profile_redirect
def password_reset_done(request):
    return TemplateResponse(request, 'auth/password_reset_done.html')

def password_change_done(request):
    return TemplateResponse(request, 'auth/password_change_done.html')
