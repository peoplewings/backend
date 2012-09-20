from django.conf.urls import patterns, include, url

urlpatterns = patterns('locations.views',
	url(r'^edit/$', 'manage_locations'),
)
