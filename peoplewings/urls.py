from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from people.forms import *
from django.contrib import *
import settings
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'landing.views.welcome', name='home'),
    # Registration patterns:
    url(r'^register/$', 'registration.views.register',    {'form_class':CustomRegisterForm, 'backend':'people.backends.default.DefaultBackend'}, name='registration_register'),
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'registration/login.html'}),
    #url(r'^logout/$','django.contrib.auth.views.logout',{'template_name':'registration/login.html'}),
    url(r'^', include('registration.backends.default.urls')),

    url(r'^users/', include('people.urls')),
    url(r'^ajax/', include('ajax.urls')),
    # url(r'^profile/$', include('people.urls'))
    # Examples:
    # url(r'^$', 'peoplewings.views.home', name='home'),
    # url(r'^peoplewings/', include('peoplewings.foo.urls')),


    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	
	# Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
# Static files patterns for development:
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
