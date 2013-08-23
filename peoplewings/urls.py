from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *
from tastypie.api import Api


from peoplewings.apps.registration.api import UserSignUpResource, ActivationResource, LoginResource, LogoutResource, AccountResource, ForgotResource, ControlResource, FacebookLoginResource
from peoplewings.apps.people.api import UserProfileResource, UniversityResource, ContactResource, PhotoCompletedResource, PhotosResource, AlbumsResource, ReferencesResource
from peoplewings.apps.locations.api import CityResource, RegionResource, CountryResource
from peoplewings.apps.wings.api import WingResource, WingNamesResource
from peoplewings.apps.feedback.api import FeedbackResource
from peoplewings.apps.cropper.api import CroppedResource, CropcompletedResource, CropbigResource, CropsmallResource
from peoplewings.apps.notifications.api import NotificationsListResource, NotificationsThreadResource

#Here we registre the resources...
admin.autodiscover()
v1_api=Api(api_name='v1')
#Registration
v1_api.register(UserSignUpResource())
v1_api.register(ActivationResource())
v1_api.register(LoginResource())
v1_api.register(LogoutResource())
v1_api.register(AccountResource())
v1_api.register(ForgotResource())
v1_api.register(ControlResource())
v1_api.register(FacebookLoginResource())
#Profile
v1_api.register(UserProfileResource())
v1_api.register(UniversityResource())
v1_api.register(ContactResource())
v1_api.register(PhotoCompletedResource())
v1_api.register(PhotosResource())
v1_api.register(AlbumsResource())
v1_api.register(ReferencesResource())
#Wings
v1_api.register(WingResource())
v1_api.register(WingNamesResource())
#Locations
v1_api.register(CityResource())
v1_api.register(RegionResource())
v1_api.register(CountryResource())
#Feedback
v1_api.register(FeedbackResource())
#Notifications
v1_api.register(NotificationsListResource())
v1_api.register(NotificationsThreadResource())
#Cropp
v1_api.register(CroppedResource())
v1_api.register(CropcompletedResource())
v1_api.register(CropbigResource())
v1_api.register(CropsmallResource())


urlpatterns = patterns('',
    url(r'^$', 'peoplewings.apps.landing.views.welcome', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('peoplewings.apps.registration.backends.custom.urls')),
    url(r'^ajax/', include('peoplewings.apps.ajax.urls')),
    url(r'^cropper/', include('peoplewings.apps.cropper.urls')),
    # API resources here...
    (r'^api/', include(v1_api.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files patterns for development:
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
