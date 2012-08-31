from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from people.forms import CustomRegisterForm
from peoplewings.utils import my_upload_success_handler, my_crop_success_handler

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'landing.views.welcome', name='home'),

    # Authentication patterns:
    url(r'^register/$', 'registration.views.register',    {'form_class':CustomRegisterForm, 'backend':'people.backends.default.DefaultBackend'}, name='registration_register'),
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'registration/login.html'}),
    url(r'^', include('registration.backends.default.urls')),

    # Apps patterns
    url(r'^users/', include('people.urls')),
    url(r'^ajax/', include('ajax.urls')),
    url(r'^wings/', include('wings.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	# Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files patterns for development:
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
