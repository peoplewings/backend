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
                content['msg'] = "Account created"
                data['email'] = json.loads(response.content)['data']
                content['code'] = 200
                content['status'] = True
                content['data'] = data                
                return self.create_response(request, content, response_class = HttpResponse)
            except BadRequest, e:
                content = {}
                errors = {}
                content['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                content['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)                               
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    content['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False                    
                    return self.create_response(request, content, response_class = HttpResponse)
                else: 
                    content = {}
                    errors = {}
                    content['msg'] = "Error in some fields"
                    errors['errors'] = json.loads(e.response)                
                    content['code'] = 410
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
            except BadParameters, e:
                # This exception occurs when the provided key has expired
                content = {}
                errors = {}
                content['msg'] = "Emails don't match"               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                content['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ExistingUser, e:
                # This exception occurs when the provided key has expired
                content = {}
                errors = {}
                content['msg'] = "The email is already being used"               
                content['code'] = 400
                content['status'] = False
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

    def custom_serialize(self, errors):
        return errors.get('activation')

    def error_response(self, errors, request):
        serialized = self.custom_serialize(errors)
        raise ImmediateHttpResponse(response=self._meta.serializer.serialize(serialized, 'application/json', None))

    def obj_create(self, bundle, request=None, **kwargs):
        request.POST = bundle.data
        self.is_valid(bundle,request)
        if bundle.errors:
            self.error_response(bundle.errors, request)
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
                content = {}
                data = {}
                content['msg'] = "Account activated"                
                content['code'] = 200
                content['status'] = True
                return self.create_response(request, content, response_class = HttpResponse)
            except BadRequest, e:
                content = {}
                errors = {}
                content['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                content['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                content['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ActivationCompleted:
                # This exception occurs when the account has already been activated
                content = {}
                errors = {}
                content['msg'] = "The activation key has been already used"               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except NotAKey:
                # This exception occurs when the provided key has not a valid format
                content = {}
                errors = {}
                content['msg'] = "The activation key is not a valid key"               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    content['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse) 
                else:               
                    content = {}
                    errors = {}
                    content['msg'] = "Error in some fields"
                    errors['errors'] = json.loads(e.response)                
                    content['code'] = 410
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
            except IntegrityError, e:
                content = {}
                errors = {}
                content['msg'] = json.loads(e.response.content)                              
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)               
            except KeyExpired:
                # This exception occurs when the provided key has expired
                content = {}
                errors = {}
                content['msg'] = "The provided key has expired"              
                content['code'] = 410
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
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

    def custom_serialize(self, errors):
        return errors.get('auth')

    def error_response(self, errors, request):
        serialized = self.custom_serialize(errors)
        raise ImmediateHttpResponse(response=self._meta.serializer.serialize(serialized, 'application/json', None))

    def obj_create(self, bundle, request=None, **kwargs):
        self.is_valid(bundle,request)
        if bundle.errors:
            self.error_response(bundle.errors, request)        
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
                content = {}
                data = {}
                content['msg'] = "Logged in"
                data['xAuthToken'] = json.loads(response.content)['token']                
                content['code'] = 200
                content['status'] = True
                content['data'] = data                
                return self.create_response(request, content, response_class = HttpResponse)
            except BadRequest, e:
                content = {}
                errors = {}
                content['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                content['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                content['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    content['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse) 
                else:               
                    content = {}
                    errors = {}
                    content['msg'] = "Error in some fields"
                    errors['errors'] = json.loads(e.response)                
                    content['code'] = 410
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
            except AuthFail, e:
                content = {}
                errors = {}
                content['msg'] = "Username/password do not match any user in the system"              
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)               
            except NotActive, e:
                content = {}
                errors = {}
                content['msg'] = "Inactive user"              
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)                
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

    def post_list(self, request=None, **kwargs):
        #destroy this session data
        if (logout(request)):
            return True
        raise ImmediateHttpResponse(response=HttpApplicationError())

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)
                content = {}
                data = {}
                content['msg'] = "Logout complete"                
                content['code'] = 200
                content['status'] = True
                return self.create_response(request, content, response_class = HttpResponse)
            except BadRequest, e:
                content = {}
                errors = {}
                content['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                content['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                content['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    content['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse) 
                elif (isinstance(e.response, HttpUnauthorized)):
                    content = {}
                    errors = {}
                    content['msg'] = "Unauthorized"                               
                    content['code'] = 413
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpApplicationError)):
                    content = {}
                    errors = {}
                    content['msg'] = "Can't logout"                               
                    content['code'] = 400
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                else:               
                    content = {}
                    errors = {}
                    content['msg'] = "Error"               
                    content['code'] = 400
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
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
       
    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('GET', 'PUT', 'DELETE'):  # 1.
            return object_list.filter(id = request.user.id)
        return []

    def put_list(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)
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

    def get_detail(self, request, **kwargs):
        response = super(AccountResource, self).get_detail(request, **kwargs)    
        data = json.loads(response.content)
        content = {}  
        content['msg'] = 'Account shown'      
        content['status'] = True
        content['code'] = 200
        content['data'] = data
        return self.create_response(request, content, response_class=HttpResponse)
        
    def put_detail(self, request, **kwargs):
        if request and 'password' in request.raw_post_data and self.is_valid_password(json.loads(request.raw_post_data)['password'], request):
            pass
        else:
            errors = {}
            content = {} 
            errors['password'] = ['Incorrect password']            
            content['msg'] = 'Cannot update'       
            content['status'] = False
            content['code'] = 200
            content['errors'] = errors
            return self.create_response(request, content, response_class=HttpResponse)

        response = super(AccountResource, self).patch_detail(request, **kwargs)  
        content = {} 
        content['msg'] = 'Account updated'       
        content['status'] = True
        content['code'] = 200
        return self.create_response(request, content, response_class=HttpResponse)

    def delete_detail(self, request, **kwargs):
        if request and 'password' in request.raw_post_data and self.is_valid_password(json.loads(request.raw_post_data)['password'], request):
            pass
        else:
            errors = {}
            content = {} 
            errors['password'] = ['Incorrect password']            
            content['msg'] = 'Cannot delete'       
            content['status'] = False
            content['code'] = 200
            content['errors'] = errors
            return self.create_response(request, content, response_class=HttpResponse)

        super(AccountResource, self).delete_detail(request, **kwargs)    
        contents = {}
        data = {}       
        contents['msg'] = 'Account deleted'        
        contents['status'] = True
        contents['code'] = 200
        return self.create_response(request, contents, response_class = HttpResponse)

    def is_valid_password(self, password, request):
        print authenticate(username=request.user.email, password=password)
        if (authenticate(username=request.user.email, password=password)):
            return True
        return False

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)
                return response
            except BadRequest, e:
                content = {}
                errors = {}
                contents['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                contents['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                content['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    content['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse) 
                elif (isinstance(e.response, HttpUnauthorized)):
                    content = {}
                    errors = {}
                    content['msg'] = "Unauthorized"                               
                    content['code'] = 413
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpApplicationError)):
                    content = {}
                    errors = {}
                    contents['msg'] = "Can't update"                               
                    content['code'] = 400
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpBadRequest)):
                    content = {}
                    errors = {}
                    content['msg'] = "Error"               
                    content['code'] = 400
                    content['status'] = False
                    errors = json.loads(e.response.content)['accounts']
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
                else:
                    content = {}
                    content['msg'] = "Error"               
                    content['code'] = 400
                    content['status'] = False                                 
                    return self.create_response(request, content, response_class = HttpResponse)
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

    def custom_serialize(self, errors):
        return errors.get('forgot')

    def error_response(self, errors, request):
        serialized = self.custom_serialize(errors)
        raise ImmediateHttpResponse(response=self._meta.serializer.serialize(serialized, 'application/json', None))

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

    def obj_create(self, bundle, request, **kwargs):
        self.is_valid(bundle,request)
        if bundle.errors:
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
            if len(bundle.data['new_password']) < 1: raise BadRequest('{"newPassword":["This field cannot be empty"]}')
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
                print response.content
                content = {}
                data = {}
                contents['msg'] = json.loads(response.content)['data']                                
                content['code'] = 200
                content['status'] = True
                return self.create_response(request, content, response_class = HttpResponse)
            except BadRequest, e:
                content = {}
                errors = {}
                contents['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.args[0])               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                contents['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                contents['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    contents['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpUnauthorized)):
                    content = {}
                    errors = {}
                    contents['msg'] = "Unauthorized"                               
                    content['code'] = 413
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpApplicationError)):
                    content = {}
                    errors = {}
                    contents['msg'] = "Error"                               
                    content['code'] = 400
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse) 
                else:               
                    content = {}
                    errors = {}
                    contents['msg'] = "Error in some fields"
                    errors['errors'] = json.loads(e.response)                
                    content['code'] = 410
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
            except DeletedAccount, e:
                content = {}
                errors = {}
                contents['msg'] = e.args[0]                               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except BadParameters, e:
                content = {}
                errors = {}
                contents['msg'] = e.args[0]['data']                                               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except NotAKey:
                content = {}
                errors = {}
                contents['msg'] = "Not a key"                               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)
            except KeyExpired:
                content = {}
                errors = {}
                contents['msg'] = "The key has expired"                               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse)                            
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)
        return wrapper       

   
