from django.conf.urls import patterns, include, url

urlpatterns = patterns('people.views',
    url(r'^(?P<people_id>\d+)/$', 'viewProfile'),
    url(r'^(?P<people_id>\d+)/enterEditProfile/$', 'enterEditProfile'),
    url(r'^(?P<people_id>\d+)/editProfile/$', 'editProfile'),
    url(r'^(?P<people_id>\d+)/viewAccountSettings/$', 'viewAccountSettings'),
    url(r'^(?P<people_id>\d+)/editAccountSettings/$', 'editAccountSettings'),
    url(r'^(?P<people_id>\d+)/delete/$', 'delete'),
)