from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'landing.views.welcome', name='home'),
    url(r'^', include('registration.backends.default.urls')),
    # Examples:
    # url(r'^$', 'peoplewings.views.home', name='home'),
    # url(r'^peoplewings/', include('peoplewings.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
