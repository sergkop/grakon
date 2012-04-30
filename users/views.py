# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from grakon.context_processors import project_settings
from grakon.utils import authenticated_ajax_post
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

        in_contacts = False
        if self.request.user.is_authenticated():
            in_contacts = self.request.profile.has_contact(profile)

        self.info = profile.info()

        ctx.update({
            'tab': self.tab,
            'tabs': tabs,
            'profile': profile,
            'own_profile': own_profile,
            'in_contacts': in_contacts,
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

# TODO: need more strict condition
edit_profile = login_required(EditProfileView.as_view())

def remove_account(request):
    if request.user.is_authenticated():
        subject = u'[УДАЛЕНИЕ АККАУНТА] %s - %s %s' % (request.user.username,
                request.profile.first_name, request.profile.last_name)

        context = project_settings(request)
        context.update({'profile': request.profile})
        html = render_to_string('letters/remove_account.html', context)

        send_email(subject, settings.ADMIN_EMAIL, html)
        return HttpResponse('ok')

    return HttpResponse(u'Чтобы удалить аккаунт, необходимо войти в систему')

@login_required
def profile(request):
    """ Redirects user to profile page after logging in (used to overcome django limitation) """
    return redirect(request.profile.get_absolute_url())

# TODO: limit the number of messages User can send daily (also depends on his points)
# TODO: add points for sending message
@authenticated_ajax_post
def send_message(request):
    title = request.POST.get('title', '')
    body = request.POST.get('body', '')
    if title == '':
        return HttpResponse(u'Необходимо указать тему письма')
    if body == '':
        return HttpResponse(u'Сообщение не должно быть пустым')

    try:
        receiver_id = int(request.POST.get('id', ''))
        receiver = Profile.objects.get(id=receiver_id)
    except ValueError, Profile.DoesNotExist:
        return HttpResponse(u'Получатель указан неверно')

    

    
    ctx = { 
        'title': title,
        'body': body,
        'show_email': 'show_email' in request.POST,
        #'link': u'%s%s' % (settings.URL_PREFIX, reverse('profile', kwargs={'username': self.from_user.username})),
    }
    if show_email:
        ctx['from_user'] = self.from_user
    message = render_to_string('mail/notification.txt', ctx)
    mail_title = u'Пользователь %s написал вам сообщение' % self.from_user.username 

    try:
        send_mail(mail_title, message, settings.DEFAULT_FROM_EMAIL, [to_user.email], fail_silently=False)
    except SMTPException:
        return u'Невозможно отправить сообщение'
    else:
        Message.objects.create(from_user=self.request.profile, to_user=to_user.get_profile(), title=title, body=body, show_email=show_email)

    # TODO: clean body html (leave text only?)
    # TODO: set reply to user's email if he gave permission or write not to answer email

    return HttpResponse('ok')
