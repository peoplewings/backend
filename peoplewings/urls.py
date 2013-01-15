from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *
from tastypie.api import Api


from peoplewings.apps.registration.api import UserSignUpResource, ActivationResource, LoginResource, LogoutResource, AccountResource, ForgotResource
from peoplewings.apps.people.api import UserProfileResource, UserLanguageResource, LanguageResource, UserUniversityResource, UniversityResource, SocialNetworkResource, UserSocialNetworkResource, InstantMessageResource, UserInstantMessageResource, RelationshipResource, ReferenceResource
from peoplewings.apps.locations.api import CityResource, RegionResource, CountryResource
from peoplewings.apps.wings.api import AccomodationsResource, WingResource
from peoplewings.apps.feedback.api import FeedbackResource
from peoplewings.apps.cropper.api import CroppedResource
from peoplewings.apps.notifications.api import NotificationsListResource, NotificationsThreadResource

#Here we registre the resources...
admin.autodiscover()

v1_api=Api(api_name='v1')
v1_api.register(UserSignUpResource())
v1_api.register(ActivationResource())
v1_api.register(UserProfileResource())
v1_api.register(LoginResource())
v1_api.register(LogoutResource())
v1_api.register(AccountResource())
v1_api.register(ForgotResource())
v1_api.register(UserLanguageResource())
v1_api.register(LanguageResource())
v1_api.register(UserUniversityResource())
v1_api.register(UniversityResource())
v1_api.register(UserSocialNetworkResource())
v1_api.register(SocialNetworkResource())
v1_api.register(UserInstantMessageResource())
v1_api.register(InstantMessageResource())
v1_api.register(CityResource())
v1_api.register(RegionResource())
v1_api.register(CountryResource())
v1_api.register(AccomodationsResource())
v1_api.register(FeedbackResource())
v1_api.register(RelationshipResource())
v1_api.register(CroppedResource())
v1_api.register(ReferenceResource())
v1_api.register(NotificationsListResource())
v1_api.register(NotificationsThreadResource())
v1_api.register(WingResource())

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
