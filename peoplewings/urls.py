from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *
from tastypie.api import Api

from peoplewings.apps.registration.api import UserResource

admin.autodiscover()

v1_api=Api(api_name='v1')
v1_api.register(UserResource())

urlpatterns = patterns('',
    url(r'^$', 'peoplewings.apps.landing.views.welcome', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    # API resources here...
    (r'^api/', include(v1_api.urls)),	
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files patterns for development:
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
