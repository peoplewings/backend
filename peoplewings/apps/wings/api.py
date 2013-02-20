
from django.conf.urls.defaults import url
from django.views.decorators.csrf import csrf_exempt
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.cache import *
from django import http as djangoHttp
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.models import AnonymousUser
from datetime import date, datetime

from tastypie import fields
from tastypie import *
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse, NotFound
from tastypie.http import HttpBadRequest, HttpApplicationError, HttpAccepted, HttpResponse, HttpForbidden
from tastypie.utils import trailing_slash, dict_strip_unicode_keys
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS

from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.wings.models import Accomodation, PublicTransport, Wing
from peoplewings.apps.wings.forms import *
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.locations.models import City, Region, Country
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.locations.api import CityResource

from wings.domain import *

from pprint import pprint

import json

class PublicTransportResource(ModelResource):
	class Meta:
		object_class = PublicTransport
		queryset = PublicTransport.objects.all()
		allowed_methods = ['get']
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		validation = FormValidation(form_class=PublicTransportForm)

class WingResource(ModelResource):
	wing_type = fields.CharField()
	class Meta:
		object_class = Wing
		queryset = Wing.objects.all()
		detail_allowed_methods = []
		list_allowed_methods = ['get']
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		include_resource_uri = False
		fields = ['name', 'id']
		resource_name='wings'

	def get_list_validate(self, request):
		errors = {}
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		invalid = {"type":"INVALID_FIELD", "extras":[]}
		if(request.GET.has_key('profile')):
			prof = request.GET['profile']
			try:
				up = UserProfile.objects.get(pk= prof)
			except:
				invalid['extras'].append('profile')
		else:
			field_req['extras'].append('profile')

		if len(field_req['extras']) > 0:
			errors.append(field_req)

		if len(invalid['extras']) > 0:
			errors.append(invalid)

		return errors

	def get_list(self, request, **kwargs):
		errors = None
		try:
			errors = self.get_list_validate(request)		
			if len(errors) > 0:
					return self.create_response(request, {"status" : False, "errors": errors}, response_class = HttpResponse)

			prof = UserProfile.objects.get(pk=request.GET['profile'])
			w = Wing.objects.filter(author=prof)		
			objects = []
			for i in w:
				aux = ShortWings()
				aux.idWing = i.pk
				aux.wingName = i.name
				aux.wingType = i.get_class_name()
				objects.append(aux.jsonable())
			data = {}
			data['items'] = objects
			return self.create_response(request, {"status":True, "data": data}, response_class = HttpResponse)
		except Exception, e:
			print e
			return self.create_response(request, {"status":False, "errors": [{"type":"INTERAL_ERROR"}]}, response_class = HttpResponse)

	def dehydrate_wing_type(self, bundle):
		return bundle.obj.get_type()

	def alter_list_data_to_serialize(self, request, data):
		return data["objects"]

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
	



class AccomodationsResource(ModelResource):
	city = fields.ToOneField(CityResource, 'city', full=True, null=True)
	#public_transport = fields.ToManyField(PublicTransportResource, 'public_transport', full=True, null=True)

	class Meta:
		object_class = Accomodation
		queryset = Accomodation.objects.all()
		detail_allowed_methods = ['get', 'delete', 'put']
		list_allowed_methods = ['get', 'post']
		resource_name = 'profiles/me/accomodations'
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		#include_resource_uri = True
		validation = FormValidation(form_class=AccomodationForm)
		filtering = {
			"city": ALL_WITH_RELATIONS,
			"date_start": ['gte'],
			"date_end": ['lte'],
			"capacity": ['exact'],
			"is_request": ['exact'],
			"status": ['exact'],
			"best_days": ['exact'],
			"bus": ['exact'],
			"tram": ['exact'],
			"train": ['exact'],
			"others": ['exact'],
			"smoking": ['exact'],
			"i_have_pet": ['exact'],
			"pets_allowed": ['exact'],
			"live_center": ['exact'],
			"wheelchair": ['exact'],
		}

	def apply_authorization_limits(self, request, object_list=None):
		if request.method not in ('GET'):
			up = UserProfile.objects.get(user=request.user)
			return object_list.filter(author=up)
		return object_list

	def obj_create(self, bundle, request=None, **kwargs):
		if 'profile_id' not in kwargs:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["profile"]}]}, response_class=HttpResponse)
		
		self.is_valid(bundle)
		if bundle.errors:
			self.error_response(bundle.errors, request)
 
		up = UserProfile.objects.get(user=request.user)
 
		# creamos la ciudad si hace falta
		data = bundle.data['city']
		city = City.objects.saveLocation(**data)
		bundle = self.full_hydrate(bundle)

		name = bundle.data['name']
		address = bundle.data['address']
		number = bundle.data['number']
		postal_code = bundle.data['postal_code']

		# creamos la wing accomodation
		a = Accomodation.objects.create(city=city, author=up, name=name, address=address, number=number, postal_code=postal_code)
		del bundle.data['city']
		del bundle.data['address']
		del bundle.data['name']
		del bundle.data['number']
		del bundle.data['postal_code']

		forbidden_fields_update = ['author_id', 'id']                
		for key, value in bundle.data.items():
			if hasattr(a, key) and key not in forbidden_fields_update: setattr(a, key, value)
		trans = PublicTransport.objects.all()
		a.public_transport = []
		for i in trans:
			if i.name in bundle.data:
				a.public_transport.add(i)
		a.save()

		bundle = self.build_bundle(obj=a, request=request)
		return bundle

	def get_list(self, request, **kwargs):
		if 'profile_id' not in kwargs:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["profile"]}]}, response_class=HttpResponse)
		
		up = UserProfile.objects.get(user=request.user)        
		if kwargs['profile_id'] == 'me': kwargs['profile_id'] = up.id

		is_preview = request.path.split('/')[-1] == 'preview'
		if not is_preview and int(kwargs['profile_id']) != up.id: 
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)

		try:
			accomodations = Accomodation.objects.filter(author_id=kwargs['profile_id'])
		except:
			return self.create_response(request, {"status" : False, "errors": [{"type": "INVALID_FIELD", "extras": ["profile"]}]}, response_class=HttpResponse)
		
		objects = []
		for i in accomodations:
			bundle = self.build_bundle(obj=i, request=request)
			bundle = self.full_dehydrate(bundle)
			if not is_preview:
				dic = {}
				dic['name'] = bundle.data['name']
				dic['uri'] = str.replace(bundle.data['resource_uri'], 'me', str(up.id))
				bundle.data = dic
			objects.append(bundle.data)
		return self.create_response(request, {"status":True, "data":objects})
	
	def post_list(self, request, **kwargs):
		up = UserProfile.objects.get(user=request.user)

		deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
		deserialized = self.alter_deserialized_detail_data(request, deserialized)
		bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
		updated_bundle = self.obj_create(bundle, request, **self.remove_api_resource_names(kwargs))
		location = self.get_resource_uri(updated_bundle)

		if not self._meta.always_return_data:
			a = http.HttpCreated(location=location)
		else:
			updated_bundle = self.full_dehydrate(updated_bundle)
			updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
			a = self.create_response(request, updated_bundle, response_class=http.HttpCreated, location=location)

		data = {}
		data['id'] = json.loads(a.content)['id']
		dic = {"data":data, "status":True}
		return self.create_response(request, dic)

	def get_detail(self, request, **kwargs):
		if 'profile_id' not in kwargs:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["profile"]}]}, response_class=HttpResponse)
		
		up = UserProfile.objects.get(user=request.user)
		is_preview = request.path.split('/')[-1] == 'preview'
		if not is_preview and int(kwargs['profile_id']) != up.id: 
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		
		if kwargs['profile_id'] == 'me': kwargs['profile_id'] = up.id
		try:
			a = Accomodation.objects.get(author_id=kwargs['profile_id'], pk=kwargs['wing_id'])
		except Exception, e:
			return self.create_response(request, {"status" : False, "errors": [{"type": "BAD_REQUEST"}]}, response_class=HttpResponse)
		bundle = self.build_bundle(obj=a, request=request)
		bundle = self.full_dehydrate(bundle)
		return self.create_response(request, {"status":True, "data":bundle})

	def patch_detail(self, request, **kwargs):
		return self.put_detail(request, **kwargs)    

	@transaction.commit_on_success
	def put_detail(self, request, **kwargs):
		if 'profile_id' not in kwargs:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["profile"]}]}, response_class=HttpResponse)

		deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
		deserialized = self.alter_deserialized_detail_data(request, deserialized)
		bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)

		self.is_valid(bundle)
		if bundle.errors:
			self.error_response(bundle.errors, request)
		try:
			a = Accomodation.objects.get(pk=int(kwargs['wing_id']), author=UserProfile.objects.get(user=request.user))
		except:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		if 'city' in bundle.data:
			loc = {}
			data = bundle.data['city']
			for key, value in data.items():            
				loc[key] = value
			city = City.objects.saveLocation(**loc)
			setattr(a, 'city', city)
			bundle.data.pop('city')

		forbidden_fields_update = ['author_id', 'id']
		for i in bundle.data:
			if hasattr(a, i) and i not in forbidden_fields_update:
				setattr(a, i, bundle.data.get(i))
		trans = PublicTransport.objects.all()
		a.public_transport = []
		for i in trans:
			if i.name in bundle.data.keys():
				a.public_transport.add(i)
		
		#updated_bundle = self.dehydrate(bundle)
		#updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
		a.save()
		self.save_related(bundle)
		bundle = {"status" : True}
		return self.create_response(request, bundle, response_class=HttpResponse)

	@transaction.commit_on_success
	def delete_detail(self, request, **kwargs):
		if 'profile_id' not in kwargs:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["profile"]}]}, response_class=HttpResponse)
		up = UserProfile.objects.get(user=request.user)
		try:
			a = Accomodation.objects.get(author_id=up.id, pk=kwargs['wing_id'])
		except:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		a.delete()
		bundle = self.build_bundle(data={"status": True}, request=request)
		return self.create_response(request, bundle, response_class = HttpResponse)

	def dehydrate_city(self, bundle):
		city = bundle.data['city'].obj
		region = city.region
		country = region.country
		bundle.data['city'] = {}
		bundle.data['city']['name'] = city.name
		bundle.data['city']['region'] = region.name
		bundle.data['city']['country'] = country.name
		bundle.data['city']['lat'] = city.lat
		bundle.data['city']['lon'] = city.lon
		return bundle.data['city']
	
	def full_dehydrate(self, bundle):
		format = '%Y-%m-%d'
		if bundle.obj.date_start is not None and type(bundle.obj.date_start) == unicode:
			bundle.obj.date_start = datetime.datetime.strptime(bundle.obj.date_start, format)
		if bundle.obj.date_end is not None and type(bundle.obj.date_end) == unicode:
			bundle.obj.date_end = datetime.datetime.strptime(bundle.obj.date_end, format)
		bundle = super(AccomodationsResource, self).full_dehydrate(bundle)

		bundle.data['resource_uri'] = str.replace(bundle.data['resource_uri'], 'me', str(bundle.obj.author.id))
		is_preview = bundle.request.path.split('/')[-1] == 'preview'
		if is_preview:
			del bundle.data['address']
			del bundle.data['number']
			del bundle.data['postal_code']
			del bundle.data['additional_information']
			bundle.data['resource_uri'] += '/preview'
		all_public = PublicTransport.objects.all();
		for j in all_public:
			bundle.data[j.name] = False
		for j in bundle.obj.public_transport.all():
			bundle.data[j.name] = True
		return bundle
	
	def alter_list_data_to_serialize(self, request, data):
		return data["objects"]

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
	
