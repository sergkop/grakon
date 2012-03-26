from django.conf.urls.defaults import url, patterns

from auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm

urlpatterns = patterns('auth.views',
    url(r'^register$', 'register', name='register'),
    url(r'^registration_completed$', 'registration_completed', name='registration_completed'),
    url(r'^email_not_sent$', 'email_not_sent', name='email_not_sent'),

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)$', 'activate', name='activate_account'),
    url(r'^activation_completed$', 'activation_completed', name='activation_completed'),

    url(r'^login$', 'login', name='login'),
    url(r'^logout$', 'logout', name='logout'),

    url(r'^password_reset_done$', 'password_reset_done', name='password_reset_done'),
    url(r'^password_change_done$', 'password_change_done', name='password_change_done'),
)

urlpatterns += patterns('django.contrib.auth.views',
    # The two-step password change
    url(r'^change_password$', 'password_change', name='password_change', kwargs={
            'template_name': 'auth/password_change.html',
            'password_change_form': PasswordChangeForm,
            'post_change_redirect': 'password_change_done',
    }),

    # The four-step password reset
    url(r'^password_reset$', 'password_reset', name='password_reset', kwargs={
            'template_name': 'auth/password_reset.html',
            'password_reset_form': PasswordResetForm,
            'post_reset_redirect': 'password_reset_done',
    }),
    url(r'^password_reset_complete$', 'password_reset_complete', name='password_reset_complete', kwargs={
            'template_name': 'auth/password_reset_complete.html'}),
    url(r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            'password_reset_confirm', name='password_reset_confirm', kwargs={'set_password_form': SetPasswordForm,
            'template_name': 'auth/password_reset_confirm.html'}),
)

# TODO: fix it
from django.views.generic.base import TemplateView
urlpatterns += patterns('grakon.views',
    url(r'^password_change_forbidden/$', TemplateView.as_view(template_name='auth/password_change_forbidden.html'),
        name='password_change_forbidden')
)
