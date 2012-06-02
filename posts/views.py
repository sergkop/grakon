# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from elements.participants.models import EntityParticipant
from elements.utils import entity_post_method
from elements.views import entity_base_view, participants_view
from grakon.utils import escape_html
from posts.forms import PostForm
from posts.models import EntityPost
from services.disqus import disqus_page_params

class BasePostView(object):
    template_name = 'posts/base.html'
    tab = None

    def update_context(self):
        return {}

    # TODO: this code is similar to officials and events
    def get_context_data(self, **kwargs):
        ctx = super(BasePostView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))
        self.participants_url = reverse('post_participants', args=[id])
        ctx.update(entity_base_view(self, EntityPost, id))

        tabs = [
            ('view', u'Идея', self.entity.get_absolute_url(), 'posts/view.html', ''),
            ('wall', u'Обсуждение', reverse('post_wall', args=[id]), 'disqus/comments.html', 'wall-tab'),
            ('participants', u'Участники', self.participants_url, 'elements/table_tab.html', ''),
        ]

        if ctx['is_admin']:
            tabs.append(('edit', u'Редактировать', reverse('edit_post', args=[id]),
                    'elements/edit_form.html', ''))

        ctx.update({
            'tabs': tabs,
            'post': self.entity,
            'follow_button': {
                'cancel_msg': u'Вы хотите отписаться от новостей об этой идее?',
                'cancel_btn': u'Отписаться',
                'cancel_btn_long': u'Отписаться',
                'confirm_msg': u'Вы хотите следить за этой идеей?',
                'confirm_btn': u'Следить',
                'confirm_btn_long': u'Следить',
            },
        })
        ctx.update(disqus_page_params('post/'+str(id), reverse('post_wall', args=[id]), 'posts'))
        return ctx

# TODO: show the entity to which post is refered
class PostView(BasePostView, TemplateView):
    tab = 'view'

class PostWallView(BasePostView, TemplateView):
    tab = 'wall'

class PostParticipantsView(BasePostView, TemplateView):
    tab = 'participants'

    def update_context(self):
        return participants_view(self)

# TODO: test that only admin can edit post page
class EditPostView(BasePostView, UpdateView):
    form_class = PostForm
    tab = 'edit'

    def get_object(self):
        return get_object_or_404(EntityPost, id=int(self.kwargs.get('id')))

    def get_success_url(self):
        return reverse('post', args=[self.kwargs.get('id')])

# TODO: need more strict condition
edit_post = login_required(EditPostView.as_view())

# TODO: limit the number of symbols
@entity_post_method
def add_post(request, entity):
    EntityPost.objects.add(entity, request.profile, escape_html(request.POST.get('content', '')),
            request.POST.get('url', ''), request.POST.get('opinion', ''))
    return HttpResponse('ok')
