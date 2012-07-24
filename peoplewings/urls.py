from django.conf.urls import patterns, include, url
from django.contrib import admin
from people.forms import *
from django.contrib import *
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'landing.views.welcome', name='home'),
    # Registration patterns:
    url(r'^register/$', 'registration.views.register',    {'form_class':CustomRegisterForm, 'backend':'people.backends.default.DefaultBackend'}, name='registration_register'),
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'registration/login.html'}),
    #url(r'^', include('registration.backends.default.urls')),

    url(r'^people/$', include('people.urls')),
    # url(r'^profile/$', include('people.urls'))
    # Examples:
    # url(r'^$', 'peoplewings.views.home', name='home'),
    # url(r'^peoplewings/', include('peoplewings.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	# Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
