from django.conf.urls.defaults import patterns, url

from referendum.views import AboutView, GroupsView, InitiativeGroupView, InitiativeGroupSupportersView, \
        QuestionsView, QuestionView, QuestionSupportersView

urlpatterns = patterns('',
    url(r'^referendum$', QuestionsView.as_view(), name='referendum'),
    url(r'^groups$', GroupsView.as_view(), name='referendum_groups'),
    url(r'^about_referendum$', AboutView.as_view(), name='referendum_about'),

    url(r'^question/(?P<id>\d+)$', QuestionView.as_view(), name='question'),
    url(r'^question/(?P<id>\d+)/supporters$', QuestionSupportersView.as_view(), name='question_supporters'),

    url(r'^initiative_group/(?P<id>\d+)$', InitiativeGroupView.as_view(), name='initiative_group'),
    url(r'^initiative_group/(?P<id>\d+)/supporters$', InitiativeGroupSupportersView.as_view(), name='initiative_group_participants'),
)
