from django.conf.urls import patterns, include, url


urlpatterns = patterns('peoplewings.apps.ajax.views',
	url(r'^search/university/$', 'search_university'),
	url(r'^image/delete/(?P<original_id>\d+)/$', 'delete_image'),
)