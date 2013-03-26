from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('postcards.api',
    url(r'^postcard/(?P<postcard_id>\d+)/$', 'postcard.PostcardAPI', name='postcard_single_api'),
    url(r'^postcard/$', 'postcard.PostcardAPI', name='postcard_api'),

    url(r'^postcard/(?P<postcard_id>\d+)/photo/(?P<photo_id>\d+)/$', 'postcard.PostcardAPI', name='postcard_photo_single_api', kwargs={'method':'photo'}),
    url(r'^postcard/(?P<postcard_id>\d+)/photo/$', 'postcard.PostcardAPI', name='postcard_photo_api', kwargs={'method':'photo'}),

    url(r'^postcard/(?P<postcard_id>\d+)/favorite/$', 'postcard.PostcardAPI', name='postcard_favorite_api', kwargs={'method':'favorite'}),

    url(r'^user/(?P<user_id>\d+)/$', 'user.UserAPI', name='user_api_single'),
    url(r'^user/me$', 'user.UserAPI', kwargs={'method':'me'}),
    url(r'^user/$', 'user.UserAPI', name='user_api'),

    url(r'^geofeatures/$', 'postcard.get_geofeatures', name='geofeatures_api'),

    url(r'^update_facebook_likes/$', 'postcard.update_facebook_likes', name='update_facebook_likes'),
)

urlpatterns += patterns('postcards.api',
    url(r'^register/$', 'register', name='register_api'),
)
