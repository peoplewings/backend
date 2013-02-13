
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
from django.http import HttpResponse

from peoplewings.apps.cropper.models import Cropped, Original
from peoplewings.apps.cropper.forms import CroppedForm
from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.people.models import UserProfile
from peoplewings.libs.S3Custom import S3Custom
from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from tastypie.utils import dict_strip_unicode_keys

class CroppedResource(ModelResource):
	
	
	class Meta:
		object_class = Cropped
		queryset = Cropped.objects.all()
		allowed_methods = ['post']
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		validation = FormValidation(form_class=CroppedForm)
  

	def post_detail(self, request, **kwargs):
		#kwargs = id de la original
		#raw_post_data = x, y, w, h   
		deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
		deserialized = self.alter_deserialized_detail_data(request, deserialized)
		bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
	 
		cropped_img = Cropped()

		cropped_img.original = Original.objects.get(pk=kwargs['pk'])            
		cropped_img.x = int(bundle.data['x'])
		cropped_img.y = int(bundle.data['y'])
		cropped_img.w = int(bundle.data['w'])
		cropped_img.h = int(bundle.data['h'])
		cropped_img.cropit()
		
		if cropped_img is not None:
			try:
				cropped_img.create_thumbs((244, 244), (108, 108), (48, 48))
				cropped_img.save()
				up = UserProfile.objects.get(user = request.user.pk)
				#Save the images to s3
				s3 = S3Custom()
				new_url_big = s3.upload_file(cropped_img.image_big.path, 'avatar')
				new_url_med = s3.upload_file(cropped_img.image_med.path, 'avatar')
				new_url_small = s3.upload_file(cropped_img.image_small.path, 'avatar')
				new_url_blur = s3.upload_file(cropped_img.image_med_blur.path, 'avatar')
				#Delete local and old(s3) images
				s3.delete_file(up.avatar)
				s3.delete_file(up.medium_avatar)
				s3.delete_file(up.thumb_avatar)
				s3.delete_file(up.blur_avatar)
				cropped_img.remove_local()
				#Assign the url to the avatar field in userprofile
				if new_url_big is not None and new_url_med is not None and new_url_small is not None and new_url_blur is not None:
					up.avatar = new_url_big
					up.medium_avatar = new_url_med
					up.thumb_avatar = new_url_small
					up.blur_avatar = new_url_blur
					up.save()
				else:
					return self.create_response(request, {"status":False, "error":[{"type":"INTERNAL_ERROR"}]]}, response_class = HttpResponse)            
				data = dict()
				data['url'] = up.avatar
				data['width'] = cropped_img.w
				data['height'] = cropped_img.h
				return self.create_response(request, {"status":True, "data":data}, response_class = HttpResponse)
			except Exception, e:
				return self.create_response(request, {"status":False, "error":[{"type":"INTERNAL_ERROR"}]]}, response_class = HttpResponse)
		else:
			return self.create_response(request, {"status":False, "error":[{"type":"INTERNAL_ERROR"}]]}, response_class = HttpResponse)

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
	
