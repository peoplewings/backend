##API for Notifications

from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpMethodNotAllowed
from tastypie.utils import trailing_slash

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

from peoplewings.apps.people.models import UserProfile
from models import Notifications, Requests, Invites, Messages, NotificationsAlarm

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from tastypie.utils import dict_strip_unicode_keys

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
        #validation = FormValidation(form_class=CroppedForm)
  
    def prepend_urls(self):      
        return [
            ## notifications/me (get_detail and post_detail and delete_detail)
            url(r"^(?P<resource_name>%s)/me%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('api_notifications_detail'), name="api_account_detail"),
        ] 
    
    def api_notifications_detail(self, request, **kwargs):
        return self.dipatch_detail(request, **kwargs)
            
    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('GET'):  # 1.
            prof = UserProfile.objects.get(user = request.user)
            return object_list.filter(receiver = prof)
        return []    

    def get_list(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)
    
    def get_detail(self, request, **kwargs):
        response = super(NotificationsResource, self).get_detail(request, **kwargs)    
        data = json.loads(response.content)
        content = {}  
        content['msg'] = 'Notifications shown'      
        content['status'] = True
        content['code'] = 200        
        content['data'] = data
        return self.create_response(request, content, response_class=HttpResponse)
    
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
