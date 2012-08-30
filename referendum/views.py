# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from elements.participants.models import EntityParticipant
from elements.views import entity_base_view, entity_tabs_view
from referendum.forms import QuestionForm
from referendum.models import InitiativeGroup, Question

class BaseReferendumView(object):
    template_name = 'referendum/base.html'
    tab = None

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseReferendumView, self).get_context_data(**kwargs)

        self.tabs = [
            ('questions', u'Вопросы: %i' % Question.objects.count(), reverse('referendum'), 'referendum/questions.html'),
            ('referendum_groups', u'Инициативные группы: %i' % InitiativeGroup.objects.count(), reverse('referendum_groups'), 'referendum/groups.html'),
            ('referendum_about', u'О референдуме', reverse('referendum_about'), 'referendum/about.html'),
        ]

        ctx.update(entity_tabs_view(self))

        ctx.update({
            'title': u'Референдум',
            'is_referendum_page': True,
        })
        ctx.update(self.update_context())
        return ctx

class QuestionsView(BaseReferendumView, TemplateView):
    tab = 'questions'

    def update_context(self):
        question_ids = Question.objects.order_by('-rating').values_list('id', flat=True)
        questions_data = Question.objects.info_for(question_ids, True)
        return {
            'questions': [questions_data[q_id] for q_id in question_ids],
        }

class GroupsView(BaseReferendumView, TemplateView):
    tab = 'referendum_groups'

    def update_context(self):
        group_ids = InitiativeGroup.objects.order_by('location__name').values_list('id', flat=True)
        groups_data = InitiativeGroup.objects.info_for(group_ids, True)
        return {
            'groups': [groups_data[id] for id in group_ids],
        }

class AboutView(BaseReferendumView, TemplateView):
    tab = 'referendum_about'


class BaseQuestionView(object):
    template_name = 'referendum/question_base.html'
    tab = None

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseQuestionView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))

        ctx.update(entity_base_view(self, Question, {'id': id}))

        self.tabs = [
            ('wall', u'Обсуждение: %i' % ctx['info']['comments']['count'], reverse('question', args=[id]), 'referendum/question_wall.html'),
            ('supporters', u'Поддержали: %i' % self.info['participants']['follower']['count'], reverse('question_supporters', args=[id]), 'referendum/question_supporters.html'),
        ]

        ctx.update(entity_tabs_view(self))

        ctx.update({
            'title': u'Вопрос: '+self.entity.title,
            'question': self.entity,
            'is_referendum_page': True,
        })
        return ctx

class QuestionView(BaseQuestionView, TemplateView):
    tab = 'wall'

class QuestionSupportersView(BaseQuestionView, TemplateView):
    tab = 'supporters'

class CreateQuestionView(CreateView):
    template_name = 'referendum/create_question.html'
    form_class = QuestionForm
    model = Question

    def form_valid(self, form):
        if self.request.profile.referendum != 'expert':
            return HttpResponse(u'Только эксперты могут добавлять вопросы для референдума')

        question = form.save()

        EntityParticipant.objects.add(question, self.request.profile, 'admin')
        EntityParticipant.objects.add(question, self.request.profile, 'follower')

        response = super(CreateQuestionView, self).form_valid(form)
        return response

create_question = login_required(CreateQuestionView.as_view())

class BaseInitiativeGroupView(object):
    template_name = 'referendum/group_base.html'
    tab = None

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseInitiativeGroupView, self).get_context_data(**kwargs)

        id = int(self.kwargs.get('id'))

        ctx.update(entity_base_view(self, InitiativeGroup, {'id': id}))

        self.tabs = [
            ('wall', u'Обсуждение: %i' % ctx['info']['comments']['count'], reverse('initiative_group', args=[id]), 'referendum/group_wall.html'),
            ('participants', u'Участники: %i' % self.info['participants']['follower']['count'], reverse('initiative_group_participants', args=[id]), 'referendum/group_participants.html'),
        ]

        ctx.update(entity_tabs_view(self))

        ctx.update({
            'title': u'Инициативная группа: '+self.entity.location.name,
            'group': self.entity,
            'is_referendum_page': True,
        })
        return ctx

class InitiativeGroupView(BaseInitiativeGroupView, TemplateView):
    tab = 'wall'

class InitiativeGroupSupportersView(BaseInitiativeGroupView, TemplateView):
    tab = 'participants'
