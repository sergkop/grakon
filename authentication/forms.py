# -*- coding:utf-8 -*-
import re

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
import django.contrib.auth.forms as auth_forms
from django.contrib.auth.models import User
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe

from crispy_forms.layout import Fieldset, HTML, Layout

from authentication.models import ActivationProfile
from elements.forms import location_init, resources_init
from elements.utils import form_helper
from services.email import send_email
from users.models import Profile

password_digit_re = re.compile(r'\d')
password_letter_re = re.compile(r'[a-zA-Z]')

class BaseRegistrationForm(forms.ModelForm):
    username = forms.RegexField(label=u'Имя пользователя (логин)', max_length=20, min_length=4, regex=r'^[\w\.]+$',
            help_text=u'4-20 символов (латинские буквы, цифры, подчеркивания и точки). Регистр не учитывается.')

    email = forms.EmailField(label=u'Электронная почта (email)',
            help_text=u'<b>Вам будет выслано письмо со ссылкой для активации аккаунта</b>')

    class Meta:
        model = Profile
        fields = ('username', 'last_name', 'first_name')

@resources_init
@location_init(True, u'Место жительства')
class RegistrationForm(BaseRegistrationForm):
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(render_value=False),
            help_text=u'Пароль должен быть не короче <b>8 знаков</b> и содержать по крайней мере одну латинскую букву и одну цифру')
    password2 = forms.CharField(label=u'Подтвердите пароль', widget=forms.PasswordInput(render_value=False))

    helper = form_helper('register', u'Зарегистрироваться')
    helper.form_id = 'registration_form'
    helper.layout = Layout(
        Fieldset(u'Персональные данные', 'last_name', 'first_name', 'email', 'location_select', 'resources'),
        Fieldset(u'Аккаунт', 'username', 'password1', 'password2')
    )

    #if CaptchaField:
    #    captcha = CaptchaField(label=u'Код проверки', error_messages = {'invalid': u'Неверный код проверки'},
    #            help_text=u'Пожалуйста, введите цифры и буквы с картинки слева, чтобы мы могли отличить вас от робота')

    def account_exists_error(self, msg, user):
        """ Raise username or email field error if corresponding user already exists """
        # TODO: implement it
        #if social account(s) are associated:
            # suggest to use associated accounts (links) or change/set password (check if it is set)

        raise forms.ValidationError(mark_safe(msg+
                u'<br/>Если вы зарегистрировались ранее, то можете <a href="%s">войти в систему</a> '
                u'или <a href="%s">восстановить пароль</a>' % (reverse('login'), reverse('password_reset'))
                ))

    def clean_username(self):
        try:
            user = User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            # No user with such username exists
            return self.cleaned_data['username']

        self.account_exists_error(u'Пользователь с этим именем уже <a href="%s" target="_blank">существует</a>.' % user.get_absolute_url(), user)

    def clean_email(self):
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        except User.MultipleObjectsReturned:
            # TODO: report to admin
            user = User.objects.filter(email=self.cleaned_data['email'])[0]

        self.account_exists_error(u'Пользователь с этим адресом электронной почты уже зарегистрирован', user)

    def clean_password1(self):
        password = self.cleaned_data['password1']

        if password != '':
            if len(password) < 8:
                raise forms.ValidationError(u'Пароль должен содержать не менее 8 символов')

            if password_letter_re.search(password) is None or password_digit_re.search(password) is None:
                raise forms.ValidationError(u'Пароль должен содержать по крайней мере одну латинскую букву и одну цифру')

        return password

    def clean_password2(self):
        if self.cleaned_data.get('password1', '') != self.cleaned_data['password2']:
            raise forms.ValidationError(u'Введенные вами пароли не совпадают')

        return self.cleaned_data['password2']

    # TODO: check that email domain is correct (ping it) (?)
    # TODO: collect domains from old users and warn if entered is not one of them
    def save(self):
        username, email, password = self.cleaned_data['username'], \
                self.cleaned_data['email'], self.cleaned_data.get('password1', '')

        # TODO: make sure email is still unique (use transaction)
        user = User.objects.create_user(username, email, password)

        profile = user.get_profile()
        for field in self.Meta.fields:
            setattr(profile, field, self.cleaned_data[field])
        profile.save()

        user.is_active = False
        user.save()

        ActivationProfile.objects.init_activation(user)

        for source in ['registration', 'show_name', 'resources']:
            profile.update_source_points(source)

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

        fields = ['last_name', 'first_name', 'email', 'location_select', 'username']

        if self.email_verified:
            del self.fields['email']
            fields.remove('email')

        self.helper.layout = Layout(Fieldset('', *fields))

    def account_exists_error(self, msg, user):
        """ Raise username or email field error if corresponding user already exists """
        # TODO: fix it (offer to merge accounts)
        raise forms.ValidationError(mark_safe(msg+
                u'<br/>Если вы зарегистрировались ранее, то можете <a href="%s">войти в систему</a> '
                u'или <a href="%s">восстановить пароль</a>' % (reverse('login'), reverse('password_reset'))
                ))

    def clean_username(self):
        # TODO: check if self.email_verified
        try:
            user = User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            # No user with such username exists
            return self.cleaned_data['username']

        self.account_exists_error(u'Пользователь с этим именем уже <a href="%s" target="_blank">существует</a>.' % user.get_absolute_url(), user)

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

        for source in ['registration', 'show_name', 'resources']:
            profile.update_source_points(source)

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
        self.fields['username'].label = u'Имя пользователя или электронная почта'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(u'Пожалуйста, введите корретное имя пользователя или адрес электронной почты и пароль.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(u'Эта учётная запись неактивна')
        self.check_for_test_cookie() # TODO: what is it for?
        return self.cleaned_data

# TODO: set minimum password complexity
class SetPasswordForm(auth_forms.SetPasswordForm):
    helper = form_helper('', u'Установить пароль')

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
