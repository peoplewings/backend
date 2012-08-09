from django.conf.urls import patterns, include, url

urlpatterns = patterns('people.views',
	url(r'^profile/$', 'view_profile'),
    url(r'^profile/edit/$', 'enter_edit_profile'),
    url(r'^profile/edit/basic$', 'enter_edit_basic_information'),
    url(r'^profile/formset$', 'formset_play'),
    url(r'^profile/edit/completed/$', 'edit_profile'),
    url(r'^basic/edit/completed/$', 'edit_basic_information'),
    url(r'^account/$', 'view_account_settings'),
    url(r'^account/edit/$', 'enter_edit_account_settings'),
    url(r'^account/edit/completed/$', 'edit_account_settings'),
    url(r'^search/$', 'search'),
    url(r'^delete/$', 'delete'),
)