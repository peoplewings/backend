#Registration API
from django.contrib.auth.models import User
import json
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError
from django.forms import ValidationError
from django.utils.cache import patch_cache_control

from peoplewings.apps.registration.exceptions import ActivationCompleted, NotAKey, KeyExpired, AuthFail, NotActive
from peoplewings.apps.registration.models import RegistrationProfile
from peoplewings.apps.registration.views import register, activate, login, logout   
from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.registration.forms import UserSignUpForm, ActivationForm, LoginForm
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

class UserSignUpResource(ModelResource):
    
    form_data = None
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'newuser'
        #excludes = ['is_active', 'is_staff', 'is_superuser']
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserSignUpForm)

    def obj_create(self, bundle, request=None, **kwargs):
        request.POST = bundle.data
        self.form_data = register(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')            
        return bundle

    def dehydrate(self, bundle):
        bundle.data = {}
        if self.form_data and self.form_data._errors:
            bundle.data['status'] = False
            bundle.data['code'] = 401
            bundle.data['errors'] = self.form_data._errors
        else:
            bundle.data['status'] = True
            bundle.data['code'] = 201
            bundle.data['data'] = 'Registration complete'        
        return bundle

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                # response is a HttpResponse object, so follow Django's instructions
                # to change it to your needs before you return it.
                # https://docs.djangoproject.com/en/dev/ref/request-response/
                return response
            except BadRequest, e:
                return HttpBadRequest({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ImmediateHttpResponse, e:
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)          
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper

class ActivationResource(ModelResource):
    form_data = None    
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'activation'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=ActivationForm)

    def obj_create(self, bundle, request=None, **kwargs):
        request.POST = bundle.data
        self.form_data = activate(request, 'peoplewings.apps.registration.backends.custom.CustomBackend', activation_key = bundle.data['activation_key'])        
        return bundle
        
    def dehydrate(self, bundle):
        bundle.data = {}
        bundle.data['status'] = True
        bundle.data['code'] = 201
        bundle.data['data'] = 'Activation complete'        
        return bundle

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                # response is a HttpResponse object, so follow Django's instructions
                # to change it to your needs before you return it.
                # https://docs.djangoproject.com/en/dev/ref/request-response/
                return response
            except BadRequest, e:
                return HttpBadRequest({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ActivationCompleted:
                # This exception occurs when the account has already been activated
                bundle = {"code": 810, "status": False, "error": "The activation key has been already used"}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except NotAKey:
                # This exception occurs when the provided key has not a valid format
                bundle = {"code": 811, "status": False, "error": "The provided key is not a valid key"}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ImmediateHttpResponse, e:
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except IntegrityError, e:               
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except KeyExpired:
                # This exception occurs when the provided key has expired
                bundle = {"code": 812, "status": False, "error": "The provided key has expired"}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper

class LoginResource(ModelResource):
    form_data = None    
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'auth'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=LoginForm)

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data = login(bundle)
        return bundle
        
    def dehydrate(self, bundle):
        bundle.data['status'] = True
        bundle.data['code'] = 201       
        return bundle

    def full_dehydrate(self, bundle):
        token = bundle.data
        bundle.data = {}
        bundle.data['status'] = True
        bundle.data['code'] = 201 
        bundle.data['token'] = token      
        return bundle

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                # response is a HttpResponse object, so follow Django's instructions
                # to change it to your needs before you return it.
                # https://docs.djangoproject.com/en/dev/ref/request-response/
                return response
            except BadRequest, e:
                return HttpBadRequest({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ImmediateHttpResponse, e:
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except AuthFail, e:
                bundle = {"status":False, "code":"820", "error": "Username/password do not match any user in the system"}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except NotActive, e:
                bundle ={"status":False, "code":"821", "error": "Inactive user"}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper     

class LogoutResource(ModelResource):
    form_data = None    
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'noauth'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=LoginForm)

    def dehydrate(self, bundle):
        bundle.data = {}
        bundle.data['status'] = True
        bundle.data['code'] = 204       
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        #destroy this session data
        if (logout(request)):
            return bundle
        raise ImmediateHttpResponse(response=HttpApplicationError())

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                # response is a HttpResponse object, so follow Django's instructions
                # to change it to your needs before you return it.
                # https://docs.djangoproject.com/en/dev/ref/request-response/
                response.status_code = 204
                return response
            except BadRequest, e:
                return HttpBadRequest({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500                
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpUnauthorized)):
                    bundle = {"code": 401, "status": False, "error":"Unauthorized"}
                    return self.create_response(request, bundle, response_class = HttpUnauthorized)
                if (isinstance(e.response, HttpApplicationError)):
                    bundle = {"code": 401, "status": False, "error":"Error"}
                    return self.create_response(request, bundle, response_class = HttpApplicationError)
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)
        return wrapper     
    
class AccountResource(ModelResource):       
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        resource_name = 'account'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        
    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('GET'):  # 1.
            import pprint
            pprint.pprint (object_list.__dict__)
            pprint.pprint (request.user)
            return object_list.filter(id = request.user.id)
        return []
