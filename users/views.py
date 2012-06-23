# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from grakon.utils import authenticated_ajax_post, escape_html
from elements.participants.models import participant_in
from elements.utils import table_data
from elements.views import entity_base_view, entity_tabs_view
from services.email import send_email
from users.forms import MessageForm, ProfileForm
from users.models import Message, Profile

class BaseProfileView(object):
    template_name = 'profiles/base.html'
    tab = None # 'view' or 'edit'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseProfileView, self).get_context_data(**kwargs)

        username = self.kwargs.get('username')

        ctx.update(entity_base_view(self, Profile, {'username': username}))

        self.tabs = [
            ('view', u'Инфо', reverse('profile', args=[username]), '', 'profiles/view.html'),
            ('tasks', u'Задачи: %i' % self.info['tasks']['admin']['count'], reverse('profile_tasks', args=[username]), '', 'tasks/list.html'),
            ('projects', u'Проекты: %i' % self.info['projects']['admin']['count'], reverse('profile_projects', args=[username]), '', 'projects/list.html'),
            ('ideas', u'Идеи: %i' % self.info['ideas']['admin']['count'], reverse('profile_ideas', args=[username]), '', 'ideas/list.html'),
            #('contacts', u'В контактах у', reverse('profile_contacts', args=[username]), '', 'elements/table.html'),
        ]

        ctx.update(entity_tabs_view(self))

        self.own_profile = (self.entity==self.request.profile)

        # TODO: UX_HACK
        if len(ctx['info']['locations']['entities']) > 0:
            location = ctx['info']['locations']['entities'][0]['instance']
        else:
            location = None

        ctx.update({
            'title': unicode(self.entity),
            'profile': self.entity,
            'is_admin': self.own_profile,
            'location': location,
        })
        ctx.update(self.update_context())
        return ctx

class ProfileView(BaseProfileView, TemplateView):
    tab = 'view'

    def update_context(self):
        return {'message_form': MessageForm()}

class ProfileTasksView(BaseProfileView, TemplateView):
    tab = 'tasks'

    def update_context(self):
        # TODO: take data from cache?
        return table_data(self.request, 'tasks', participant_in(self.entity, 'admin', 'tasks'))

class ProfileProjectsView(BaseProfileView, TemplateView):
    tab = 'projects'

    def update_context(self):
        return table_data(self.request, 'projects', participant_in(self.entity, 'admin', 'projects'))

class ProfileIdeasView(BaseProfileView, TemplateView):
    tab = 'ideas'

    def update_context(self):
        return table_data(self.request, 'ideas', participant_in(self.entity, 'admin', 'ideas'))

#class ProfileContactsView(BaseProfileView, TemplateView):
#    tab = 'contacts'
#
#    def update_context(self):
#        return table_data(self.request, 'participants', self.entity.get_follower)

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
@authenticated_ajax_post
def send_message(request):
    form = MessageForm(request.POST)

    # TODO: what happens if title in post data is longer than model field max_length?
    if not form.is_valid():
        # TODO: show error messages u'Необходимо указать тему письма', u'Сообщение не должно быть пустым'
        return HttpResponse('Форма заполнена неверно')

    try:
        recipient_id = int(request.POST.get('id', ''))
        recipient = Profile.objects.select_related('user').get(id=recipient_id)
    except ValueError, Profile.DoesNotExist:
        return HttpResponse(u'Получатель указан неверно')

    title = escape_html(form.cleaned_data['title'])
    body = escape_html(form.cleaned_data['body'])
    show_email = form.cleaned_data['show_email']

    subject = u'Пользователь %s написал вам сообщение' % unicode(request.profile)
    ctx = {
        'title': title,
        'body': body,
        'show_email': show_email,
        'sender': request.profile,
    }
    send_email(recipient, subject, 'letters/message.html', ctx, 'message', 'noreply',
            reply_to=request.profile.user.email if show_email else None)

    Message.objects.create(sender=request.profile, receiver=recipient, title=title,
            body=body, show_email=show_email)

    return HttpResponse('ok')
