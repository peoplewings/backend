##API for Notifications
import json
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpMethodNotAllowed
from tastypie.utils import trailing_slash
from tastypie.utils import dict_strip_unicode_keys

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.utils.cache import patch_cache_control
from django.contrib.auth.models import User
from django.conf.urls import url
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.db.models import Q

from peoplewings.apps.people.models import UserProfile
from models import Notifications, Requests, Invites, Messages, NotificationsAlarm

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

from domain import *

class NotificationsResource(ModelResource):
    
    class Meta:
        object_class = Notifications
        queryset = Notifications.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True                    

    def get_list(self, request, **kwargs):
        ## We are doin it the hard way
        try:
            prof = UserProfile.objects.get(user = request.user)
        except:
            return self.create_response(request, {"status":False, "msg":"Not a valid user", "code":"403"}, response_class = HttpResponse)
        try:
            my_notifications = Notifications.objects.filter(Q(receiver=prof)|Q(sender=prof)).order_by('-created')
            result = []
            for i in my_notifications:
                aux = notifications_list()
                aux.reference = i.reference
                result.append(aux)
                print i.__dict__
        except Exception, e:
            return self.create_response(request, {"status":False, "msg":e, "code":"403"}, response_class = HttpResponse)
        return self.create_response(request, {"status":True, "msg":"OK", "data" : , "code":"200"}, response_class = HttpResponse)
            
        
    def get_detail(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)
    
    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)              
                return response
            except (BadRequest, fields.ApiFieldError), e:
                return http.HttpBadRequest(e.args[0])
            except ValidationError, e:
                return http.HttpBadRequest(', '.join(e.messages))
            except Exception, e:
                if hasattr(e, 'response'):
                    return e.response

                # A real, non-expected exception.
                # Handle the case where the full traceback is more helpful
                # than the serialized error.
                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise

                # Re-raise the error to get a proper traceback when the error
                # happend during a test case
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise

                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper
