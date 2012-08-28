from django.conf.urls import patterns, include, url

urlpatterns = patterns('wings.views',
	url(r'^list/$', 'list_wings'),
	url(r'^info/$', 'manage_wing_information'),
	url(r'^delete/(?P<wing_id>\d+)/$', 'delete_wing'),
)