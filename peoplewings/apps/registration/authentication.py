from tastypie.authentication import Authentication
from tastypie.http import HttpUnauthorized
from tastypie.exceptions import ImmediateHttpResponse
from peoplewings.apps.registration.views import api_token_is_authenticated

class ApiTokenAuthentication(Authentication):
    def _unauthorized(self):
        raise ImmediateHttpResponse(response=HttpUnauthorized())
        
    def is_authenticated(self, request, **kwargs):
        apitoken = api_token_is_authenticated(request, **kwargs)
        if apitoken:
            request.user = apitoken
            return True
        else:
            return self._unauthorized()

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username

class AnonymousApiTokenAuthentication(ApiTokenAuthentication):
        
    def _unauthorized(self):
        return True
