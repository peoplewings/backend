from django.conf.urls import patterns, include, url


urlpatterns = patterns('ajax.views',
	url(r'^search/university/$', 'search_university'),
)