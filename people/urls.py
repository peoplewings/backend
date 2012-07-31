from django.conf.urls import patterns, include, url

urlpatterns = patterns('people.views',
	url(r'^profile/$', 'viewProfile'),
    url(r'^profile/edit/$', 'enterEditProfile'),
    url(r'^profile/edit/completed/$', 'editProfile'),
    url(r'^account/$', 'viewAccountSettings'),
    url(r'^account/edit/$', 'enterEditAccountSettings'),
    url(r'^account/edit/completed/$', 'editAccountSettings'),
    url(r'^search/$', 'search'),
    url(r'^delete/$', 'delete'),
)