from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^add_comment$', 'elements.comments.views.add_comment', name='add_comment'),
    url(r'^remove_comment$', 'elements.comments.views.remove_comment', name='remove_comment'),

    url(r'^add_location$', 'elements.locations.views.add_location', name='add_location'),
    url(r'^remove_location$', 'elements.locations.views.remove_location', name='remove_location'),

    url(r'^add_participant$', 'elements.participants.views.add_participant', name='add_participant'),
    url(r'^remove_participant$', 'elements.participants.views.remove_participant', name='remove_participant'),

    url(r'^add_resource$', 'elements.resources.views.add_resource', name='add_resource'),
    url(r'^remove_resource$', 'elements.resources.views.remove_resource', name='remove_resource'),

    url(r'^update_text_field$', 'elements.views.update_text_field', name='update_text_field'),
)
