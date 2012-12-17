from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
		url(r'^$', 'gridcontrol.content.views.home', name='home'),
		url(r'^logged-in/$', 'gridcontrol.content.views.logged_in', name='logged_in'),
		url(r'^account/$', 'gridcontrol.content.views.account', name='account'),
		url(r'^account/logout/$', 'gridcontrol.content.views.account_logout', name='logout'),
		url(r'^gist_viewer/(?P<gist_id>[^/]+)/?', 'gridcontrol.content.views.gist_viewer', name='gist_viewer'),
		url(r'', include('social_auth.urls')),
		url(r'^admin/', include(admin.site.urls)),
)
