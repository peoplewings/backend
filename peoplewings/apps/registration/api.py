#Registration API
import json
import re

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

from peoplewings.apps.people.models import UserProfile

from peoplewings.apps.registration.exceptions import ActivationCompleted, NotAKey, KeyExpired, AuthFail, NotActive, DeletedAccount, BadParameters, ExistingUser, DupplicateEmailException
from peoplewings.apps.registration.models import RegistrationProfile
from peoplewings.apps.registration.views import register, activate, login, logout, delete_account, forgot_password, check_forgot_token, change_password
from peoplewings.apps.registration.forms import UserSignUpForm, ActivationForm, LoginForm, ForgotForm
from peoplewings.apps.registration.authentication import ApiTokenAuthentication, ControlAuthentication
from peoplewings.apps.registration.validation import ForgotValidation, AccountValidation
from peoplewings.apps.registration.signals import user_deleted

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
		self.is_valid(bundle)
		
		if bundle.errors:
			self.error_response(bundle.errors, request)
		bundle.obj = register(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')      
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
			bundle.data['data'] = bundle.obj.email        
		return bundle

	def email_validation(self, email):
		if len(email) > 7:
			if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
				return 1
		return 0

	def is_valid(self, POST):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras": []}
		too_long = {"type":"TOO_LONG", "extras": []}
		invalid = {"type":"INVALID_FIELD", "extras": []}

		if POST.has_key("hasAcceptedTerms") and isinstance(POST['hasAcceptedTerms'], bool):
			if POST['hasAcceptedTerms'] == True:
				pass
			else:
				invalid['extras'].append('hasAcceptedTerms')
		else:
			field_req['extras'].append('hasAcceptedTerms')
			
		if POST.has_key("birthdayDay"):
			if int(POST['birthdayDay']) < 1 or int(POST['birthdayDay']) > 31:
				invalid['extras'].append('birthdayDay')
		else: 
			field_req['extras'].append('birthdayDay')

		if POST.has_key("birthdayMonth"):
			if int(POST['birthdayMonth']) < 1 or int(POST['birthdayMonth']) > 12:
				invalid['extras'].append('birthdayMonth')
		else: 
			field_req['extras'].append('birthdayMonth')

		if POST.has_key("birthdayYear"):
			if int(POST['birthdayYear']) < 1900 or int(POST['birthdayYear']) > 2100:
				invalid['extras'].append('birthdayYear')
		else: 
			field_req['extras'].append('birthdayYear')

		if POST.has_key("email"):
			if not self.email_validation(POST['email']):
				invalid['extras'].append('email')
		else: 
			field_req['extras'].append('email')

		if POST.has_key("repeatEmail"):
			if POST.has_key("email") and not POST['repeatEmail'] == POST['email']:
				invalid['extras'].append('repeatEmail')
		else: 
			field_req['extras'].append('repeatEmail')

		if POST.has_key("firstName"):
			if len(POST['firstName']) < 1 or len(POST['firstName']) > 50:
				too_long['extras'].append('firstName')
		else: 
			field_req['extras'].append('firstName')

		if POST.has_key("lastName"):
			if len(POST['lastName']) < 1 or len(POST['lastName']) > 50:
				too_long['extras'].append('lastName')
		else: 
			field_req['extras'].append('lastName')

		if POST.has_key("gender"):
			if POST['gender'] not in ['Male', 'Female']:
				invalid['extras'].append('gender')
		else: 
			field_req['extras'].append('gender')

		if POST.has_key("password"):
			if len(POST['password']) < 8 or re.match("^.*(?=.*\d)(?=.*[a-zA-Z]).*$"	, POST['password']) == None:
				invalid['extras'].append('password')
		else: 
			field_req['extras'].append('password')

		if len(field_req['extras']) > 0:
			errors.append(field_req)

		if len(invalid['extras']) > 0:
			errors.append(invalid)

		if len(too_long['extras']) > 0:
			errors.append(too_long)

		if len(errors) == 0:
			return None
		return errors

	def post_list(self, request, **kwargs):
		POST = json.loads(request.raw_post_data)
		request.POST = POST
		errors = None
		errors = self.is_valid(POST)		
		if errors is not None:
			return self.create_response(request, {"status":False, "errors": errors}, response_class = HttpResponse)		
		data = register(request, POST, 'peoplewings.apps.registration.backends.custom.CustomBackend')
		result = {}
		result['email'] = data
		return self.create_response(request, {"status":True, "data": result}, response_class = HttpResponse)
		
	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)
				return response
			except BadRequest, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse) 
			except ValidationError, e:
				# Or do some JSON wrapping around the standard 500
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)                               
			except ImmediateHttpResponse, e:
				if (isinstance(e.response, HttpMethodNotAllowed)):
					content = {}
					errors = [{"type": "METHOD_NOT_ALLOWED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse)
				else: 
					content = {}
					errors = [{"type": "VALIDATION_ERROR"}]
					errors['errors'] = errors
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except BadParameters, e:
				# This exception occurs when the provided key has expired
				content = {}
				errors = [{"type": "INVALID_FIELD", "extras": ["email"]}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ValueError, e:
				# This exception occurs when the JSON is not a JSON...
				content = {}
				errors = [{"type": "JSON_ERROR"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ExistingUser, e:
				# This exception occurs when the provided key has expired
				content = {}
				errors = [{"type": "EMAIL_IN_USE"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)       
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)  

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
		self.is_valid(bundle)
		if bundle.errors:
			self.error_response(bundle.errors, request)
		bundle.obj = activate(request, 'peoplewings.apps.registration.backends.custom.CustomBackend', activation_key = bundle.data['activation_key'])        
		return bundle

	def is_valid(self, POST):
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		invalid = {"type":"INVALID", "extras":[]}

		if 'activation_key' in POST:
			r = RegistrationProfile.objects.filter(activation_key = POST['activation_key'])
			if len(r) == 0:
				invalid['extras'].append('activation_key')
		else:
			field_req['extras'].append('activation_key')
	def post_list(self, request, **kwargs):
		import pdb; pdb.set_trace()
		POST = json.loads(request.raw_post_data)
		request.POST = POST
		errors = None
		errors = self.is_valid(POST)		
		if errors is not None:
			return self.create_response(request, {"status":False, "errors": errors}, response_class = HttpResponse)		
		bundle.obj = activate(request, 'peoplewings.apps.registration.backends.custom.CustomBackend', activation_key = request.POST['activation_key'])        
		result = {}
		result['email'] = data
		return self.create_response(request, {"status":True, "data": result}, response_class = HttpResponse)
		
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
				content['status'] = True
				return self.create_response(request, content, response_class = HttpResponse)
			except BadRequest, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse) 
			except ValidationError, e:
				# Or do some JSON wrapping around the standard 500
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ValueError, e:
				# This exception occurs when the JSON is not a JSON...
				content = {}
				errors = [{"type": "JSON_ERROR"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ActivationCompleted:
				# This exception occurs when the account has already been activated
				content = {}
				errors = [{"type": "USED_KEY"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except NotAKey:
				# This exception occurs when the provided key has not a valid format
				content = {}
				errors = [{"type": "INVALID_FIELD", "extras": ["activationKey"]}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ImmediateHttpResponse, e:
				if (isinstance(e.response, HttpMethodNotAllowed)):
					content = {}
					errors = [{"type": "METHOD_NOT_ALLOWED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse)
				else: 
					content = {}
					errors = [{"type": "VALIDATION_ERROR"}]
					errors['errors'] = errors
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except IntegrityError, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse)               
			except KeyExpired:
				# This exception occurs when the provided key has expired
				content = {}
				errors = [{"type": "EXPIRED_KEY"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse)

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
		self.is_valid(bundle)
		if bundle.errors:
			self.error_response(bundle.errors, request)        
		bundle.data = login(bundle)
		return bundle
		
	def dehydrate(self, bundle):
		bundle.data['status'] = True
		bundle.data['code'] = 201       
		return bundle

	def full_dehydrate(self, bundle):
		token = bundle.data['token']
		user = bundle.data['idUser']
		bundle.data = {}
		bundle.data['status'] = True
		bundle.data['code'] = 201 
		bundle.data['token'] = token
		bundle.data['account'] = user  
		return bundle

	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)
				content = {}
				data = {}
				data['xAuthToken'] = json.loads(response.content)['token']
				data['idAccount'] = json.loads(response.content)['account']
				content['status'] = True
				content['data'] = data                
				return self.create_response(request, content, response_class = HttpResponse)
			except BadRequest, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse) 
			except ValidationError, e:
				# Or do some JSON wrapping around the standard 500
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ValueError, e:
				# This exception occurs when the JSON is not a JSON...
				content = {}
				errors = [{"type": "JSON_ERROR"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ImmediateHttpResponse, e:
				if (isinstance(e.response, HttpMethodNotAllowed)):
					content = {}
					errors = [{"type": "METHOD_NOT_ALLOWED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse)
				else: 
					content = {}
					errors = [{"type": "VALIDATION_ERROR"}]
					errors['errors'] = errors
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except AuthFail, e:
				content = {}
				errors = [{"type": "INVALID_USER_OR_PASS"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)               
			except NotActive, e:
				content = {}
				errors = [{"type": "INACTIVE_USER"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)                
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse) 

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
				content['status'] = True
				return self.create_response(request, content, response_class = HttpResponse)
			except BadRequest, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse) 
			except ValidationError, e:
				# Or do some JSON wrapping around the standard 500
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ValueError, e:
				# This exception occurs when the JSON is not a JSON...
				content = {}
				errors = [{"type": "JSON_ERROR"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ImmediateHttpResponse, e:
				if (isinstance(e.response, HttpMethodNotAllowed)):
					content = {}
					errors = [{"type": "METHOD_NOT_ALLOWED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse) 
				elif (isinstance(e.response, HttpUnauthorized)):
					content = {}
					errors = [{"type": "AUTH_REQUIRED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse)
				elif (isinstance(e.response, HttpApplicationError)):
					content = {}
					errors = [{"type": "INTERNAL_ERROR"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
				else:               
					ccontent = {}
					errors = [{"type": "INTERNAL_ERROR"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse)
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
		excludes = ['is_active', 'is_staff', 'is_superuser', 'username', 'date_joined', 'last_login']
		validation = AccountValidation()     
	   
	def apply_authorization_limits(self, request, object_list=None):
		if request and request.method in ('GET', 'PUT', 'DELETE'):  # 1.
			return object_list.filter(id = request.user.id)
		return []

	def put_list(self, request, **kwargs):
		##DO NOTHING
		return self.create_response(request, {"status":False, "errors":[{"type": "METHOD_NOT_ALLOWED"}]}, response_class = HttpResponse)
	def get_list(self, request, **kwargs):
		##DO NOTHING
		return self.create_response(request, {"status":False, "errors":[{"type": "METHOD_NOT_ALLOWED"}]}, response_class = HttpResponse)
	
	def post_list(self, request, **kwargs):
		##DO NOTHING
		return self.create_response(request, {"status":False, "errors":[{"type": "METHOD_NOT_ALLOWED"}]}, response_class = HttpResponse)
	
	def post_detail(self, request, **kwargs):
		##DO NOTHING
		return self.create_response(request, {"status":False, "errors":[{"type": "METHOD_NOT_ALLOWED"}]}, response_class = HttpResponse)

	def delete_list(self, request, **kwargs):
		##DO NOTHING
		return self.create_response(request, {"status":False, "errors":[{"type": "METHOD_NOT_ALLOWED"}]}, response_class = HttpResponse)

	def get_detail(self, request, **kwargs):
		response = super(AccountResource, self).get_detail(request, **kwargs)    
		data = json.loads(response.content)
		try:
			pf = UserProfile.objects.get(user = request.user)
		except:
			pass
		data['avatar'] = pf.thumb_avatar
		content = {}    
		content['status'] = True
		del(data['password'])
		content['data'] = data
		return self.create_response(request, content, response_class=HttpResponse)

	def dehydrate(self, bundle):
		if bundle.request.method in ('GET', 'DELETE'):
			pass
		else:
			for key, value in json.loads(bundle.request.raw_post_data)['resource'].items():
				if key in bundle.data:
					bundle.data[key] = value       
		return bundle  

	def put_detail(self, request, **kwargs):
		if request and 'currentPassword' in request.raw_post_data and self.is_valid_password(json.loads(request.raw_post_data)['currentPassword'], request):
			if 'resource' in request.raw_post_data:                
				json.loads(json.dumps(json.loads(request.raw_post_data)['resource']))
			else:
				raise ValueError()            
		else:
			errors = [{"type": "INCORRECT_PASSWORD"}]
			content = {} 
			content['status'] = False
			content['errors'] = errors
			return self.create_response(request, content, response_class=HttpResponse)

		response = self.patch_detail(request, **kwargs)  
		content = {} 
		content['msg'] = 'Account updated'       
		content['status'] = True
		return self.create_response(request, content, response_class=HttpResponse)

	def delete_detail(self, request, **kwargs):
		if request and 'currentPassword' in request.raw_post_data and self.is_valid_password(json.loads(request.raw_post_data)['currentPassword'], request):
			pass
		else:
			errors = [{"type": "INCORRECT_PASSWORD"}]
			content = {} 
			content['status'] = False
			content['errors'] = errors
			return self.create_response(request, content, response_class=HttpResponse)

		super(AccountResource, self).delete_detail(request, **kwargs) 
		user_deleted.send(sender=self.__class__, user=request.user, request=request)
		contents = {}
		data = {}       
		contents['msg'] = 'Account deleted'        
		contents['status'] = True
		return self.create_response(request, contents, response_class = HttpResponse)

	def is_valid_password(self, password, request):
		#print authenticate(username=request.user.email, password=password)
		if (authenticate(username=request.user.email, password=password)):
			return True
		return False

	def update_in_place(self, request, original_bundle, new_data):
		new_data = new_data['resource']
		if 'password' in new_data:
			password = new_data['password']
			user = request.user
			user.set_password(password)
			new_data['password'] = user.password
		if 'email' in new_data:
			try:
				existing_user = User.objects.get(email = new_data['email'])
			except:
				existing_user = None
			if existing_user and existing_user != request.user:
				raise DupplicateEmailException()
		obj = super(AccountResource, self).update_in_place(request, original_bundle, new_data)
		return obj

	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)
				return response
			except BadRequest, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse) 
			except ValidationError, e:
				# Or do some JSON wrapping around the standard 500
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ValueError, e:
				# This exception occurs when the JSON is not a JSON...
				content = {}
				errors = [{"type": "JSON_ERROR"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ImmediateHttpResponse, e:
				if (isinstance(e.response, HttpMethodNotAllowed)):
					content = {}
					errors = [{"type": "METHOD_NOT_ALLOWED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse) 
				elif (isinstance(e.response, HttpUnauthorized)):
					content = {}
					errors = [{"type": "AUTH_REQUIRED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse)
				elif (isinstance(e.response, HttpApplicationError)):
					content = {}
					errors = [{"type": "INTERNAL_ERROR"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
				else:               
					content = {}
					errors = [{"type": "INTERNAL_ERROR"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except DupplicateEmailException, e:
					ccontent = {}
					errors = [{"type": "EMAIL_IN_USE"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except Exception, e:
					ccontent = {}
					errors = [{"type": "INTERNAL_ERROR"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
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
			bundle = {"status":True}                      
		else:            
			raise KeyExpired()
		return self.create_response(request, bundle)           

	def obj_create(self, bundle, request, **kwargs):
		self.is_valid(bundle)
		if bundle.errors:
			self.error_response(bundle.errors, request)

		if bundle.data.get('email'):
			self.method = 'POST'
			try:
				user = User.objects.get(email=bundle.data['email'])
				request.user = user
			except:
				bundle.data = {}
				bundle.data['status'] = True
				return bundle

			res = forgot_password(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')
			if res:
				return bundle

			bundle.data = {}
			raise BadParameters(bundle.data)
		else:
			self.method = 'PATCH'
			if len(bundle.data['new_password']) < 8: raise BadRequest('{"newPassword":["This field cannot be empty"]}')
			change_password(bundle.data)
			return bundle

	def full_dehydrate(self, bundle):
		bundle.data = {}
		bundle.data['status'] = True
		self.method = None
		return bundle

	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)
				content = {}
				content['status'] = True
				return self.create_response(request, content, response_class = HttpResponse)
			except BadRequest, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse) 
			except ValidationError, e:
				# Or do some JSON wrapping around the standard 500
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ValueError, e:
				# This exception occurs when the JSON is not a JSON...
				content = {}
				errors = [{"type": "JSON_ERROR"}]          
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ImmediateHttpResponse, e:
				if (isinstance(e.response, HttpMethodNotAllowed)):
					content = {}
					errors = [{"type": "METHOD_NOT_ALLOWED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse) 
				elif (isinstance(e.response, HttpUnauthorized)):
					content = {}
					errors = [{"type": "AUTH_REQUIRED"}]
					content['errors'] = errors	                           
					content['status'] = False                    
					return self.create_response(request, content, response_class = HttpResponse)
				elif (isinstance(e.response, HttpApplicationError)):
					content = {}
					errors = [{"type": "INTERNAL_ERROR"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
				else:               
					content = {}
					errors = [{"type": "INTERNAL_ERROR"}]
					content['errors'] = errors               
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except DeletedAccount, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except BadParameters, e:
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except NotAKey:
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except KeyExpired:
				content = {}
				errors = [{"type": "EXPIRED_KEY"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)                         
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
		return wrapper     


class ControlResource(ModelResource):       
	
	class Meta:
		object_class = User
		queryset = User.objects.all()
		detail_allowed_methods = []
		list_allowed_methods = ['get']
		include_resource_uri = False
		resource_name = 'control'
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication =  ControlAuthentication()
		authorization = Authorization()
		always_return_data = True

	def get_list(self, request, **kwargs):
		return self.create_response(request, {"status":True, "code":200}, response_class = HttpResponse) 
   
	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)     
				return response
			except (BadRequest, fields.ApiFieldError), e:
				content = {}
				errors = [{"type":"VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except ValidationError, e:
				content = {}
				errors = [{"type": "VALIDATION_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['status'] = False
				content['errors'] = errors
				return self.create_response(request, content, response_class = HttpResponse)

		return wrapper
