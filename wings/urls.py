from django.conf.urls import patterns, include, url

urlpatterns = patterns('wings.views',
	url(r'^info/$', 'manage_wing_information'),
)