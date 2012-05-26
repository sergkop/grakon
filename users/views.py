# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from grakon.utils import authenticated_ajax_post, escape_html
from elements.utils import table_data
from services.email import send_email
from users.forms import ProfileForm
from users.models import Message, Profile

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
            ('contacts', u'В контактах у', reverse('profile_contacts', args=[profile.username]), 'elements/table.html', ''),
        ]

        if own_profile:
            tabs.append(('edit', u'Редактировать', reverse('edit_profile', args=[profile.username]),
                    'profiles/edit.html', ''))

        in_contacts = False
        if self.request.user.is_authenticated():
            in_contacts = self.request.profile.has_contact(profile)

        self.info = profile.info()

        ctx.update({
            'participants_menu_item': True,
            'tab': self.tab,
            'tabs': tabs,
            'profile': profile,
            'own_profile': own_profile,
            'is_follower': in_contacts,
            'info': self.info,
            'administered_entities': profile.admin_of(),
            'follow_button': {
                'cancel_msg': u'Вы хотите удалить этого пользователя из списка контактов?',
                'cancel_btn': u'Удалить',
                'cancel_btn_long': u'Удалить из контактов',
                'confirm_msg': u'Вы хотите добавить этого пользователя в список контактов?',
                'confirm_btn': u'Добавить',
                'confirm_btn_long': u'Добавить в контакты',
            },
        })
        ctx.update(self.update_context())
        return ctx

class ProfileView(BaseProfileView, TemplateView):
    tab = 'view'

class ProfileContactsView(BaseProfileView, TemplateView):
    tab = 'contacts'

    def update_context(self):
        return table_data(self.request, 'participants', self.profile.get_follower)

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
        # TODO: fix the way to send user notification of account deletion
        subject = u'[УДАЛЕНИЕ АККАУНТА] %s - %s %s' % (request.user.username,
                request.profile.first_name, request.profile.last_name)
        send_email(None, subject, 'letters/remove_account.html', {'profile': request.profile},
                'remove_account', 'noreply')
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

    # TODO: limit title to the maximum length allowed by model (use model form)

    try:
        recipient_id = int(request.POST.get('id', ''))
        recipient = Profile.objects.select_related('user').get(id=recipient_id)
    except ValueError, Profile.DoesNotExist:
        return HttpResponse(u'Получатель указан неверно')

    # TODO: fix it
    show_email = 'show_email' in request.POST

    subject = u'Пользователь %s написал вам сообщение' % unicode(request.profile)
    ctx = {
        'title': escape_html(title),
        'body': escape_html(body),
        'show_email': show_email,
        'sender': request.profile,
    }
    send_email(recipient, subject, 'letters/message.html', ctx, 'message', 'noreply',
            reply_to=request.profile.user.email if show_email else None)

    Message.objects.create(sender=request.profile, receiver=recipient, title=title,
            body=body, show_email=show_email)

    return HttpResponse('ok')
