# -*- coding:utf-8 -*-
from django.contrib import auth
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from social_auth.utils import setting

from authentication.forms import LoginForm, ReferendumRegistrationForm, RegistrationForm, SetPasswordForm, SocialRegistrationForm
from authentication.models import ActivationProfile
from authentication.utils import authenticated_profile_redirect
from elements.resources.models import RESOURCE_DICT

@authenticated_profile_redirect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            profile = form.save()
            return redirect('registration_completed')
    else:
        form = RegistrationForm()

        # Resource can be passed as get parameter when user is coming from main page
        resource = request.GET.get('resource', '')
        if resource in RESOURCE_DICT:
            form.fields['resources1'].initial = [resource]

    return TemplateResponse(request, 'auth/register.html', {'form': form})

@authenticated_profile_redirect
def referendum_register(request):
    if request.method == 'POST':
        form = ReferendumRegistrationForm(request.POST)

        if form.is_valid():
            profile = form.save()
            return redirect('registration_completed')
    else:
        form = ReferendumRegistrationForm()

    return TemplateResponse(request, 'auth/register.html', {'form': form})

def social_registration_pipeline(request, *args, **kwargs):
    # TODO: don't show this form if kwargs['user']
    if kwargs['user']:
        return None
    return redirect('social_registration')

def finish_social_registration(request, data, user):
    name = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
    data[name] = 5 # TODO: fix it; start with settings.SOCIAL_AUTH_PIPELINE_RESUME_ENTRY
    data['kwargs']['user'] = user
    data['kwargs']['is_new'] = True
    request.session[name] = data

    return redirect('socialauth_complete', backend=data['backend'])

def social_registration(request):
    name = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
    data = request.session.get(name)

    if not data:
        return redirect('login')

    details = data['kwargs']['details']
    response = data['kwargs']['response']

    email = details['email']
    location = None

    # Check whether email is verified
    if data['backend'] == 'google-oauth2':
        email_verified = data['kwargs']['response']['verified_email']
        link = response['link']
        picture = response['picture']
        gender = response['gender']
    elif data['backend'] == 'facebook':
        email_verified = True
        link = response['link']
        picture = response['picture']
        gender = response['gender']
        # TODO: use location to autofill form field (hometown/location);
    elif data['backend'] == 'vkontakte-oauth2':
        email_verified = False
        link = 'http://vk.com/id' + str(response['user_id'])
        picture = response['photo']
        gender = ''
        # TODO: get more data http://vk.com/developers.php?oid=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BF%D0%BE%D0%BB%D0%B5%D0%B9_%D0%BF%D0%B0%D1%80%D0%B0%D0%BC%D0%B5%D1%82%D1%80%D0%B0_fields

    # TODO: use link, picture, gender

    # Check if account with this email already exists
    try:
        user = User.objects.get(email=email)
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        pass
    else:
        if email_verified:
            return finish_social_registration(request, data, user)
        else:
            pass # TODO: what to do?

    form_params = {'email_verified': email_verified}
    if email_verified:
        form_params['email'] = email

    if request.method == 'POST':
        form = SocialRegistrationForm(request.POST, **form_params)

        if form.is_valid():
            profile = form.save()

            if email_verified:
                return finish_social_registration(request, data, profile.user)
            else:
                # TODO: redirect to registration_completed before logging in
                return finish_social_registration(request, data, profile.user)

            # TODO: if email needs to be confirmed, redirect to registration_completed or /complete/<backend>/,
            #       else - profile
            return redirect('registration_completed')
    else:
        form = SocialRegistrationForm(**form_params)

    form.initial['first_name'] = details['first_name']
    form.initial['last_name'] = details['last_name']

    if not email_verified:
        form.initial['email'] = email

    return TemplateResponse(request, 'auth/register.html', {'form': form})

@authenticated_profile_redirect
def activate(request, activation_key):
    try:
        activation_profile = ActivationProfile.objects.filter(activation_key=activation_key) \
                .select_related('user').latest()
    except ActivationProfile.DoesNotExist:
        return TemplateResponse(request, 'auth/activation_fail.html')

    if activation_profile.activation_key_expired():
        return TemplateResponse(request, 'auth/activation_expired.html')

    if request.method == 'POST':
        form = SetPasswordForm(activation_profile.user, request.POST)

        if form.is_valid():
            form.save()
            activation_profile.activate()
            backend = auth.get_backends()[0] # TODO: is it ok?
            activation_profile.user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            auth.login(request, activation_profile.user)

            profile = activation_profile.user.get_profile()
            if profile.referendum != '':
                return redirect('referendum')

            return redirect('profile')
    else:
        form = SetPasswordForm(activation_profile.user)

    return TemplateResponse(request, 'auth/set_password.html', {'form': form})

@authenticated_profile_redirect
def social_activate(request, activation_key):
    try:
        profile = ActivationProfile.objects.filter(activation_key=activation_key) \
                .select_related('user').latest()
    except ActivationProfile.DoesNotExist:
        return TemplateResponse(request, 'auth/activation_fail.html')

    if profile.activation_key_expired():
        return TemplateResponse(request, 'auth/activation_expired.html')

    profile.activate()
    backend = auth.get_backends()[0] # TODO: is it ok?
    profile.user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
    auth.login(request, profile.user)
    return redirect('profile')

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
