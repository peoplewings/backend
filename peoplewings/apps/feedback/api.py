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

	def know_teh_browser(self, user_agent):
		must_have = {'Firefox':'Firefox', 'Seamonkey':'Seamonkey', 'Chrome':'Chrome', 'Chromium':'Chromium', 'Safari':'Safari', 'Opera':'Opera', 'Internet Explorer':';MSIE', 'Googlebot':'Googlebot'}
		must_not_have = {'Firefox':['Seamonkey'], 'Seamonkey':[None], 'Chrome':['Chromium'], 'Chromium':[None], 'Safari':['Chrome','Chromium'], 'Opera':[None], 'Internet Explorer':[None], 'Googlebot':['Googlebot']}
		for key, value in must_have.items():
			if user_agent.find(value) != -1:
				if must_not_have[key]:
					breaker = 0
					for key2 in must_not_have[key]:                    
							if user_agent.find(key2) != -1:
								breaker = 1
				if breaker == 0:
					return value                        
		return None
		
		
	def obj_create(self, bundle, request=None, **kwargs):
		browser = self.know_teh_browser(bundle.request.META['HTTP_USER_AGENT'])
		return super(FeedbackResource, self).obj_create(bundle, request=None, user=bundle.request.user, browser = browser)

	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)                
				response = callback(request, *args, **kwargs)
				contents = {}       
				contents['status'] = True
				return self.create_response(request, contents, response_class = HttpResponse)
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
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse)
			except ValueError, e:
				# This exception occurs when the JSON is not a JSON...
				content = {}
				errors = [{"type": "JSON_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
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
				elif (isinstance(e.response, HttpBadRequest)):
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
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR"}]
				content['errors'] = errors               
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse)
		return wrapper    
   

   
