from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
		url(r'^$', 'gridcontrol.content.views.home', name='home'),
		url(r'^logged-in/$', 'gridcontrol.content.views.logged_in', name='logged_in'),
		url(r'^account/$', 'gridcontrol.content.views.account', name='account'),
		url(r'^account/gists$', 'gridcontrol.content.views.account_gists', name='account_gists'),
		url(r'^account/debug$', 'gridcontrol.content.views.bot_debug', name='bot_debug'),
		url(r'^account/logout/$', 'gridcontrol.content.views.account_logout', name='logout'),
		url(r'^view_code/(?P<userid>\d+)/?', 'gridcontrol.content.views.view_code', name='view_code'),
		url(r'^use_gist/(?P<gist_id>[^/]+)/?', 'gridcontrol.content.views.use_gist', name='use_gist'),
		url(r'^gist_viewer/(?P<gist_id>[^/]+)/?', 'gridcontrol.content.views.gist_viewer', name='gist_viewer'),
		url(r'', include('social_auth.urls')),
		url(r'^admin/', include(admin.site.urls)),
)
