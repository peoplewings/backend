from django.conf.urls import patterns, include, url


urlpatterns = patterns('ajax.views',
	url(r'^search/university/$', 'search_university'),
	url(r'^upload/image/$', 'upload_image'),
	url(r'^upload/avatar/$', 'crop_avatar'),
)