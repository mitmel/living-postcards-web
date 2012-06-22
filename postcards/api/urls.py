from django.conf.urls.defaults import *

urlpatterns = patterns('postcards.api',
    url(r'^postcard/(?P<postcard_id>\d+)(?P<format>\.\w*)/$', 'postcard.PostcardAPI'),
    url(r'^postcard/(?P<postcard_id>\d+)/$', 'postcard.PostcardAPI', name='postcard_api_single'),
    url(r'^postcard/$', 'postcard.PostcardAPI', name='postcard_api'),
)
