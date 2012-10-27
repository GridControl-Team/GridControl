from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
		url(r'^$', 'gridcontrol.content.views.home', name='home'),
		# url(r'^gridcontrol/', include('gridcontrol.foo.urls')),
		# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
		url(r'', include('social_auth.urls')),
		url(r'^admin/', include(admin.site.urls)),
)
