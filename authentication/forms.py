# -*- coding:utf-8 -*-
import random
import re

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
import django.contrib.auth.forms as auth_forms
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe

from crispy_forms.layout import Fieldset, HTML, Layout

from authentication.models import ActivationProfile
from elements.locations.forms import location_init
from elements.resources.forms import resources_init
from elements.utils import form_helper
from services.email import send_email
from users.models import Profile

password_digit_re = re.compile(r'\d')
password_letter_re = re.compile(u'[a-zA-Zа-яА-Я]')

class BaseRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label=u'Электронная почта (email)',
            help_text=u'Вам будет выслано письмо со ссылкой для активации аккаунта')

    class Meta:
        model = Profile
        fields = ('last_name', 'first_name', 'intro')

@resources_init
@location_init(True, u'Место жительства')
class RegistrationForm(BaseRegistrationForm):

    helper = form_helper('register', u'Зарегистрироваться')
    helper.form_id = 'registration_form'
    helper.layout = Layout(
        Fieldset('', 'last_name', 'first_name', 'intro', 'email', 'location_select', 'resources1'),
    )

    def clean_email(self):
        # TODO: lowercase email?
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        except User.MultipleObjectsReturned:
            # TODO: report to admin
            user = User.objects.filter(email=self.cleaned_data['email'])[0]

        # TODO: implement it
        #if social account(s) are associated:
            # suggest to use associated accounts (links) or change/set password (check if it is set)

        raise forms.ValidationError(mark_safe(
                u'Пользователь с этим адресом электронной почты уже зарегистрирован'
                u'<br/>Если вы зарегистрировались ранее, то можете <a href="%s">войти в систему</a> '
                u'или <a href="%s">восстановить пароль</a>' % (reverse('login'), reverse('password_reset'))
                ))

    # TODO: check that email domain is correct (ping it) (?)
    # TODO: collect domains from old users and warn if entered is not one of them
    def save(self):
        email = self.cleaned_data['email']
        username = sha_constructor(email+str(random.random())).hexdigest()[:20]

        # TODO: make sure email is still unique (use transaction)
        user = User.objects.create_user(username, email)

        profile = user.get_profile()
        for field in self.Meta.fields:
            setattr(profile, field, self.cleaned_data[field])
        profile.save()

        user.is_active = False
        user.save()

        ActivationProfile.objects.init_activation(user)

        return profile

# TODO: add next hidden field
@location_init(True, u'Место жительства')
class SocialRegistrationForm(BaseRegistrationForm):
    helper = form_helper('social_registration', u'Зарегистрироваться')
    helper.form_id = 'registration_form'

    def __init__(self, *args, **kwargs):
        self.email_verified = kwargs.pop('email_verified')
        self.email = kwargs.pop('email', None)

        super(SocialRegistrationForm, self).__init__(*args, **kwargs)

        fields = ['last_name', 'first_name', 'email', 'location_select']

        if self.email_verified:
            del self.fields['email']
            fields.remove('email')

        self.helper.layout = Layout(Fieldset('', *fields))

    def account_exists_error(self, msg, user):
        """ Raise email field error if corresponding user already exists """
        # TODO: fix it (offer to merge accounts)
        raise forms.ValidationError(mark_safe(msg+
                u'<br/>Если вы зарегистрировались ранее, то можете <a href="%s">войти в систему</a> '
                u'или <a href="%s">восстановить пароль</a>' % (reverse('login'), reverse('password_reset'))
                ))

    def clean_email(self):
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        except User.MultipleObjectsReturned:
            # TODO: report to admin
            user = User.objects.filter(email=self.cleaned_data['email'])[0]

        self.account_exists_error(u'Пользователь с этим адресом электронной почты уже зарегистрирован', user)

    def save(self):
        # TODO: consider both values of self.email_verified

        if not self.email_verified:
            self.email = self.cleaned_data['email']

        # TODO: make sure email is still unique (use transaction)
        user = User.objects.create_user(self.cleaned_data['username'], self.email)

        profile = user.get_profile()
        for field in self.Meta.fields:
            setattr(profile, field, self.cleaned_data[field])
        profile.save()

        if self.email_verified:
            pass # TODO: send email notifying registration
        else:
            user.is_active = False
            user.save()
            ActivationProfile.objects.init_activation(user)

        return profile

class LoginForm(auth_forms.AuthenticationForm):
    helper = form_helper('login', u'Войти')
    helper.form_id = 'login_form'
    helper.layout = Layout(
        Fieldset('', 'username', 'password'),
        HTML(r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'),
    )

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = u'Электронная почта'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(u'Пожалуйста, введите корретный адрес электронной почты и пароль')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(u'Эта учётная запись неактивна')
        self.check_for_test_cookie() # TODO: what is it for?
        return self.cleaned_data

class SetPasswordForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(render_value=False),
            help_text=u'Пароль должен быть не короче <b>8 знаков</b> и содержать по крайней мере одну букву и одну цифру')
    password2 = forms.CharField(label=u'Подтвердите пароль', widget=forms.PasswordInput(render_value=False))

    helper = form_helper('', u'Установить пароль')
    helper.form_id = 'set_password_form'

    def __init__(self, user, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['username'].initial = user.email # this field is used by browsers to save login credentials

    def clean_password1(self):
        password = self.cleaned_data['password']

        if password != '':
            if len(password) < 8:
                raise forms.ValidationError(u'Пароль должен содержать не менее 8 символов')

            if password_letter_re.search(password) is None or password_digit_re.search(password) is None:
                raise forms.ValidationError(u'Пароль должен содержать по крайней мере одну латинскую букву и одну цифру')

        return password

    def clean_password2(self):
        if self.cleaned_data.get('password', '') != self.cleaned_data['password2']:
            raise forms.ValidationError(u'Введенные вами пароли не совпадают')

        return self.cleaned_data['password2']

    def save(self):
        self.user.set_password(self.cleaned_data['password'])
        self.user.save()
        return self.user

# TODO: set minimum password complexity
class PasswordChangeForm(auth_forms.PasswordChangeForm):
    helper = form_helper('password_change', u'Сменить пароль')

class PasswordResetForm(auth_forms.PasswordResetForm):
    helper = form_helper('password_reset', u'Восстановить пароль')

    def save(self, **kwargs):
        for user in self.users_cache:
            ctx = {
                'uid': int_to_base36(user.id),
                'user': user,
                'token': kwargs['token_generator'].make_token(user),
                'URL_PREFIX': settings.URL_PREFIX,
            }
            send_email(user.get_profile(), u'Смена пароля на grakon.org', 'letters/password_reset_email.html',
                    ctx, 'password_reset', 'noreply')
