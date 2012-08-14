from django.conf.urls import patterns, include, url

urlpatterns = patterns('people.views',
	url(r'^profile/$', 'view_profile'),
    url(r'^profile/edit/basic/$', 'manage_basic_information'),
    url(r'^profile/edit/contact/$', 'manage_contact_information'),
    url(r'^profile/edit/likes/$', 'manage_likes_information'),
    url(r'^account/$', 'view_account_settings'),
    url(r'^account/edit/$', 'enter_edit_account_settings'),
    url(r'^account/edit/completed/$', 'edit_account_settings'),
    url(r'^search/$', 'search'),
    url(r'^delete/$', 'delete'),
)