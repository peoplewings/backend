#Registration API
import json

from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
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

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer 
from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.feedback.models import Feedback
from peoplewings.apps.feedback.validation import FeedbackValidation
    
class FeedbackResource(ModelResource):         
    class Meta:
        object_class = Feedback
        queryset = Feedback.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'feedback'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True        
        validation = FeedbackValidation()

    def know_teh_browser(user_agent):
        must_have = {'Firefox':'Firefox', 'Seamonkey':'Seamonkey', 'Chrome':'Chrome', 'Chromium':'Chromium', 'Safari':'Safari', 'Opera':'Opera', 'Internet Explorer':';MSIE', 'Googlebot':'Googlebot'}
        must_not_have = {'Firefox':'Seamonkey', 'Seamonkey':None, 'Chrome':'Chromium', 'Chromium':None, 'Safari':['Chrome','Chromium'], 'Opera':None, 'Internet Explorer':None, 'Googlebot':'Googlebot'}
        return user_agent
        
        
    def obj_create(self, bundle, request=None, **kwargs):
        print bundle.request.META['HTTP_USER_AGENT']
        return super(FeedbackResource, self).obj_create(bundle, request=None, user=bundle.request.user)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)                
                response = callback(request, *args, **kwargs)
                contents = {}
                contents['msg'] = 'Feedback submited'               
                contents['code'] = 200
                contents['status'] = True
                return self.create_response(request, contents, response_class = HttpResponse)
            except BadRequest, e:
                contents = {}
                errors = {}
                contents['msg'] = e.args[0]               
                contents['code'] = 400
                contents['status'] = False
                return self.create_response(request, contents, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                contents = {}
                errors = {}
                contents['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                contents['code'] = 410
                contents['status'] = False
                contents['error'] = errors
                return self.create_response(request, contents, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                print e
                contents = {}
                errors = {}
                contents['msg'] = "No JSON could be decoded"               
                contents['code'] = 411
                contents['status'] = False
                return self.create_response(request, contents, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    contents = {}
                    errors = {}
                    contents['msg'] = "Method not allowed"                               
                    contents['code'] = 412
                    contents['status'] = False
                    return self.create_response(request, contents, response_class = HttpResponse) 
                elif (isinstance(e.response, HttpUnauthorized)):
                    contents = {}
                    errors = {}
                    contents['msg'] = "Unauthorized"                               
                    contents['code'] = 413
                    contents['status'] = False
                    return self.create_response(request, contents, response_class = HttpResponse)
                elif (isinstance(e.response, HttpApplicationError)):
                    contents = {}
                    errors = {}
                    contents['msg'] = "Can't update"                               
                    contents['code'] = 400
                    contents['status'] = False
                    return self.create_response(request, contents, response_class = HttpResponse)
                elif (isinstance(e.response, HttpBadRequest)):
                    contents = {}
                    errors = {}
                    contents['msg'] = "Error"               
                    contents['code'] = 400
                    contents['status'] = False
                    errors = json.loads(e.response.content)['accounts']
                    contents['error'] = errors
                    return self.create_response(request, contents, response_class = HttpResponse)
                else:
                    contents = {}
                    contents['msg'] = "Error"               
                    contents['code'] = 400
                    contents['status'] = False                                 
                    return self.create_response(request, contents, response_class = HttpResponse)
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)
        return wrapper    
   

   
