import base64
import hmac
import time
import uuid

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from tastypie.http import HttpUnauthorized
from tastypie.authentication import Authentication

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

try:
    import python_digest
except ImportError:
    python_digest = None

try:
    import oauth2
except ImportError:
    oauth2 = None

try:
    import oauth_provider
except ImportError:
    oauth_provider = None

class ApiTokenAuthentication(Authentication):
    """
    Handles API Token auth, in which an user provide just a temporary
    token using the 'HTTP-X' headers.
    """

    def _unauthorized(self):
        response = HttpUnauthorized()
        response['WWW-Authenticate'] = 'Token'
        return response

    def is_authenticated(self, request, **kwargs):
        """
        Finds the user with the API Token.
        """
        if not request.META.get('HTTP_AUTHORIZATION'):
            return self._unauthorized()

        try:
            http_authorization = request.META['HTTP_AUTHORIZATION']
            (auth_type, data) = http_authorization.split(' ', 1)

            if auth_type != 'Token':
                return self._unauthorized()
        except:
            return self._unauthorized()

        # Get api_token.
        from peoplewings.libs.customauth.models import ApiToken

        try:
            api_token = ApiToken.objects.get(token=data)
        except ApiToken.DoesNotExist:
            return self._unauthorized()

        # Check if still valid.
        if not api_token.is_valid():
            return self._unauthorized()

        request.user = api_token.user
        return True
