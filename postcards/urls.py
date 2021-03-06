from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'postcards.views.home', name='home'),
    url(r'^context.js$', 'postcards.views.context_js', name='context_js'),
    url(r'^facebook_channel.html$', 'postcards.views.facebook_channel_html', name='facebook_channel_html'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^api/', include('postcards.api.urls')), 
)
