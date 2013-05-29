from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *
from tastypie.api import Api


from peoplewings.apps.registration.api import UserSignUpResource, ActivationResource, LoginResource, LogoutResource, AccountResource, ForgotResource, ControlResource, FacebookLoginResource
from peoplewings.apps.people.api import UserProfileResource, UniversityResource, ContactResource, PhotoAlbumsResource, PhotosResource
from peoplewings.apps.locations.api import CityResource, RegionResource, CountryResource
from peoplewings.apps.wings.api import WingResource
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
v1_api.register(FacebookLoginResource())
v1_api.register(ControlResource())
#People
v1_api.register(UserProfileResource())
v1_api.register(UniversityResource())
v1_api.register(ContactResource())
v1_api.register(PhotoAlbumsResource())
v1_api.register(PhotosResource())
#Locations
v1_api.register(CityResource())
v1_api.register(RegionResource())
v1_api.register(CountryResource())
#Feedback
v1_api.register(FeedbackResource())
#Crop
v1_api.register(CroppedResource())
v1_api.register(CropcompletedResource())
v1_api.register(CropbigResource())
v1_api.register(CropsmallResource())
#Notifications
v1_api.register(NotificationsListResource())
v1_api.register(NotificationsThreadResource())
#Wings
v1_api.register(WingResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),	
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files patterns for development:
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
