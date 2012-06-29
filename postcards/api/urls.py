from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('postcards.api',
    url(r'^postcard/(?P<postcard_id>\d+)/$', 'postcard.PostcardAPI', name='postcard_single_api'),
    url(r'^postcard/$', 'postcard.PostcardAPI', name='postcard_api'),

    url(r'^postcard/(?P<postcard_id>\d+)/photo/(?P<photo_id>\d+)/$', 'postcard.PostcardAPI', name='postcard_photo_single_api', kwargs={'method':'photo'}),
    url(r'^postcard/(?P<postcard_id>\d+)/photo/$', 'postcard.PostcardAPI', name='postcard_photo_api', kwargs={'method':'photo'}),
)

urlpatterns += patterns('postcards.api',
    url(r'^register/$', 'register', name='register_api'),
)
