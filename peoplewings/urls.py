from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from people.forms import CustomRegisterForm

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'landing.views.welcome', name='home'),

    # Authentication patterns:
    url(r'^register/$', 'registration.views.register',    {'form_class':CustomRegisterForm, 'backend':'people.backends.default.DefaultBackend'}, name='registration_register'),
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'registration/login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^activate/complete/$', 'landing.views.welcome', name='home'),
    url(r'^', include('registration.backends.default.urls')),

    # Apps patterns
    url(r'^users/', include('people.urls')),
    url(r'^ajax/', include('ajax.urls')),
    url(r'^wings/', include('wings.urls')),
    url(r'^search/', include('search.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	# Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files patterns for development:
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
