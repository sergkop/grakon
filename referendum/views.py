# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.views.generic.base import TemplateView

from elements.views import entity_base_view, entity_tabs_view
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
        })
        ctx.update(self.update_context())
        return ctx

class QuestionsView(BaseReferendumView, TemplateView):
    tab = 'questions'

    def update_context(self):
        question_ids = Question.objects.values_list('id', flat=True)
        return {
            'questions': Question.objects.info_for(question_ids, True).values(),
        }

class GroupsView(BaseReferendumView, TemplateView):
    tab = 'referendum_groups'

    def update_context(self):
        group_ids = InitiativeGroup.objects.order_by('location__name').values_list('id', flat=True)
        return {
            'groups': InitiativeGroup.objects.info_for(group_ids, True).values(),
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
        })
        return ctx

class QuestionView(BaseQuestionView, TemplateView):
    tab = 'wall'

class QuestionSupportersView(BaseQuestionView, TemplateView):
    tab = 'supporters'


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
        })
        return ctx

class InitiativeGroupView(BaseInitiativeGroupView, TemplateView):
    tab = 'wall'

class InitiativeGroupSupportersView(BaseInitiativeGroupView, TemplateView):
    tab = 'participants'
