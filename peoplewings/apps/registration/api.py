#Registration API
import json

from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError
from tastypie.utils import trailing_slash
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.utils.cache import patch_cache_control
from django.contrib.auth.models import User
from django.conf.urls import url

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer

from peoplewings.apps.registration.exceptions import ActivationCompleted, NotAKey, KeyExpired, AuthFail, NotActive, DeletedAccount, BadParameters, ExistingUser
from peoplewings.apps.registration.models import RegistrationProfile
from peoplewings.apps.registration.views import register, activate, login, logout, delete_account, forgot_password, check_forgot_token, change_password
from peoplewings.apps.registration.forms import UserSignUpForm, ActivationForm, LoginForm, AccountForm, ForgotForm
from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.registration.validation import ForgotValidation

class UserSignUpResource(ModelResource):
    
    form_data = None
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'newuser'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserSignUpForm)

    def custom_serialize(self, errors):
        return errors.get('newuser')

    def error_response(self, errors, request):
        serialized = self.custom_serialize(errors)
        raise ImmediateHttpResponse(response=self._meta.serializer.serialize(serialized, 'application/json', None))
        
    def obj_create(self, bundle, request=None, **kwargs):
        request.POST = bundle.data
        self.is_valid(bundle,request)
        if bundle.errors:
            self.error_response(bundle.errors, request)

        bundle.obj = register(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')      
        return bundle

    def dehydrate(self, bundle):
        print bundle.data
        bundle.data = {}
        if self.form_data and self.form_data._errors:
            bundle.data['status'] = False
            bundle.data['code'] = 401
            bundle.data['errors'] = self.form_data._errors
        else:
            bundle.data['status'] = True
            bundle.data['code'] = 201
            bundle.data['data'] = bundle.obj.email        
        return bundle

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)
                content = {}
                data = {}
                data['msg'] = "Account created"
                data['email'] = json.loads(response.content)['data']
                content['code'] = 200
                content['status'] = True
                content['data'] = data                
                return self.create_response(request, content, response_class = HttpResponse)
            except BadRequest, e:
                content = {}
                errors = {}
                errors['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                errors['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)                               
            except ImmediateHttpResponse, e:
                content = {}
                errors = {}
                errors['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.response)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except BadParameters, e:
                # This exception occurs when the provided key has expired
                content = {}
                errors = {}
                errors['msg'] = "Emails don't match"               
                content['code'] = 400
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                errors['msg'] = "No JSON could be decoded"               
                content['code'] = 400
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ExistingUser, e:
                # This exception occurs when the provided key has expired
                content = {}
                errors = {}
                errors['msg'] = "The email is already being used"               
                content['code'] = 400
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)       
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
        bundle.obj = activate(request, 'peoplewings.apps.registration.backends.custom.CustomBackend', activation_key = bundle.data['activation_key'])        
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
                return HttpResponse({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except ActivationCompleted:
                # This exception occurs when the account has already been activated
                bundle = {"code": 810, "status": False, "error": "The activation key has been already used"}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except NotAKey:
                # This exception occurs when the provided key has not a valid format
                bundle = {"code": 811, "status": False, "error": "The provided key is not a valid key"}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except IntegrityError, e:               
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpResponse)
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

    @transaction.commit_on_success
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
                return HttpResponse({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except AuthFail, e:
                bundle = {"status":False, "code":"820", "error": "Username/password do not match any user in the system"}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except NotActive, e:
                bundle ={"status":False, "code":"821", "error": "Inactive user"}
                return self.create_response(request, bundle, response_class = HttpResponse)
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

    @transaction.commit_on_success
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
                return HttpResponse({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500                
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpUnauthorized)):
                    bundle = {"code": 401, "status": False, "error":"Unauthorized"}
                    return self.create_response(request, bundle, response_class = HttpResponse)
                if (isinstance(e.response, HttpApplicationError)):
                    bundle = {"code": 401, "status": False, "error":"Error"}
                    return self.create_response(request, bundle, response_class = HttpResponse)
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)
        return wrapper     
    
class AccountResource(ModelResource):       
    method = None    
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['get', 'put', 'delete']
        include_resource_uri = False
        resource_name = 'accounts'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        excludes = ['id', 'is_active', 'is_staff', 'is_superuser', 'username', 'password', 'date_joined', 'last_login']
        validation = FormValidation(form_class=AccountForm)
     
    def prepend_urls(self):      
        return [
            ## accounts/me (get_detail and post_detail and delete_detail)
            url(r"^(?P<resource_name>%s)/(?P<id_user>\w[\w-]*)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('api_account_detail'), name="api_account_detail"),
        ]

    def api_account_detail(self, request, **kwargs):
        if kwargs['id_user'] == 'me':
            kwargs.pop('id_user')                
        return self.dispatch_detail(request, **kwargs)

    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]
       
    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('GET', 'PUT', 'DELETE'):  # 1.
            return object_list.filter(id = request.user.id)
        return []

    def get_list(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)
    
    def post_list(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)
    
    def post_detail(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)

    def delete_list(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)
    
    def put_detail(self, request, **kwargs):
        self.method = 'PUT'
        return super(AccountResource, self).patch_detail(request, **kwargs)    

    def full_dehydrate(self, bundle):         
        if self.method and self.method == 'PUT':
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 202
            self.method = None           
        elif self.method and self.method == 'DELETE':
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 202
            bundle.data['data'] = 'Account deleted'
            self.method = None
        return super(AccountResource, self).full_dehydrate(bundle)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)
                
                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                return response
            except BadRequest, e:
                return HttpResponse({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500                
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except DeletedAccount, e:
                return self.create_response(request, e.args[0], response_class = HttpResponse)
            except BadParameters, e:
                return self.create_response(request, e.args[0], response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpUnauthorized)):
                    bundle = {"code": 401, "status": False, "error":"Unauthorized"}
                    return self.create_response(request, bundle, response_class = HttpResponse)
                if (isinstance(e.response, HttpApplicationError)):
                    bundle = {"code": 401, "status": False, "error":"Error"}
                    return self.create_response(request, bundle, response_class = HttpResponse)
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)
        return wrapper    
    
class ForgotResource(ModelResource):       
    
    method = None
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post','get']
        include_resource_uri = False
        resource_name = 'forgot'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        validation = ForgotValidation()

    def build_filters(self, filters=None):
        if 'forgotToken' not in filters:
            bundle = '{"forgotToken":["This field is required"]}'
            raise BadRequest(bundle) 
        return super(ForgotResource, self).build_filters(filters)

    def get_list(self, request=None, **kwargs):
        self.method = 'GET'
        if hasattr(request, 'GET'):
            # Grab a mutable copy.
            filters = request.GET.copy()
            self.build_filters(filters=filters)
        if check_forgot_token(filters, 'peoplewings.apps.registration.backends.custom.CustomBackend'):                             
            bundle = {"code":200, "status":True, "data":"The link is valid"}                      
        else:            
            raise KeyExpired()
        return self.create_response(request, bundle)           

    @transaction.commit_on_success
    def obj_create(self, bundle, request, **kwargs):
        self.is_valid(bundle,request)
        if bundle.errors:
            bundle.errors = bundle.errors['forgot']
            self.error_response(bundle.errors, request)

        if bundle.data.get('email'):
            self.method = 'POST'
            try:
                user = User.objects.get(email=bundle.data['email'])
                request.user = user
            except:
                bundle.data = {}
                bundle.data['status'] = False
                bundle.data['code'] = 400
                bundle.data['data'] = 'Invalid email'
                raise BadParameters(bundle.data)

            res = forgot_password(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')
            if res:
                return bundle

            bundle.data = {}
            bundle.data['status'] = False
            bundle.data['code'] = 400
            bundle.data['errors'] = 'Invalid email'
            raise BadParameters(bundle.data)
        else:
            self.method = 'PATCH'
            change_password(bundle.data)
            return bundle

    def full_dehydrate(self, bundle):
        if self.method and self.method == 'POST':
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 202
            bundle.data['data'] = 'Email sent'
        elif self.method and self.method == 'PATCH':
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 200
            bundle.data['data'] = 'Password changed'      
        self.method = None
        return bundle

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                return response
            except BadRequest, e:
                bundle = {"code": 777, "status": False, "errors": json.loads(e.args[0])}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500                
                bundle = {"code": 777, "status": False, "errors": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except DeletedAccount, e:
                return self.create_response(request, e.args[0], response_class = HttpResponse)
            except BadParameters, e:
                return self.create_response(request, e.args[0], response_class = HttpResponse)
            except NotAKey:
                bundle = {"code": 777, "status": False, "errors": "Invalid link"}
                return self.create_response(request, bundle, response_class = HttpResponse)
            except KeyExpired:
                bundle = {"code":412, "status":False, "data":"The key has expired"}
                return self.create_response(request, bundle, response_class = HttpResponse)            
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpUnauthorized)):
                    bundle = {"code": 401, "status": False, "errors":"Unauthorized"}
                    return self.create_response(request, bundle, response_class = HttpResponse)
                if (isinstance(e.response, HttpApplicationError)):
                    bundle = {"code": 401, "status": False, "errors":"Error"}
                    return self.create_response(request, bundle, response_class = HttpResponse)
                else:
                    bundle = {"code": 777, "status": False, "errors": json.loads(e.response.content)}
                    return self.create_response(request, bundle, response_class = HttpResponse) 
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)
        return wrapper       

   
