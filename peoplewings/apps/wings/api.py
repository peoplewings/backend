
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
from django.db.models import Q

from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.wings.models import Accomodation, PublicTransport, Wing
from peoplewings.apps.wings.forms import *
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.locations.models import City, Region, Country
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.locations.api import CityResource
from wings.domain import AccomodationWingEditable

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
			w = Wing.objects.filter(Q(author=prof)&Q(active=True))		
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
		up_target = UserProfile.objects.filter(pk=kwargs['profile_id'])

		is_preview = request.path.split('/')[-1] == 'preview'
		if not is_preview and int(kwargs['profile_id']) != up.id: 
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)

		try:
			accomodations = Accomodation.objects.filter(Q(author_id=kwargs['profile_id'])&Q(active=True)).order_by('pk')
		except:
			return self.create_response(request, {"status" : False, "errors": [{"type": "INVALID_FIELD", "extras": ["profile"]}]}, response_class=HttpResponse)
		
		objects = []
		for i in accomodations:
			if not is_preview:
				aux_wing = AccomodationWingEditable()
				aux_wing.id = i.pk		
				aux_wing.name = i.name
				aux_wing.status = i.status

				if i.date_start is None:
					aux_wing.date_start = "null"
				else:
					aux_wing.date_start = i.date_end

				if i.date_end is None:
					aux_wing.date_end = "null"
				else:
					aux_wing.date_end = i.date_end

				aux_wing.best_days = i.best_days
				city = {}
				city['lat'] = i.city.lat
				city['lon'] = i.city.lon
				city['name'] = i.city.name
				city['region'] = i.city.region.name
				city['country'] = i.city.region.country.name
				aux_wing.city = city
				aux_wing.sharing_once = i.sharing_once
				aux_wing.capacity = i.capacity

				if not i.preferred_male and not i.preferred_female:
					aux_wing.preferred_gender = 'None'
				elif i.preferred_male and not i.preferred_female:
					aux_wing.preferred_gender = 'Male'
				elif not i.preferred_male and i.preferred_female:
					aux_wing.preferred_gender = 'Female'
				elif i.preferred_male and i.preferred_female:
					aux_wing.preferred_gender = 'Both'

				aux_wing.wheelchair = i.wheelchair
				aux_wing.where_sleeping_type = i.where_sleeping_type
				aux_wing.smoking = i.smoking
				aux_wing.i_have_pet = i.i_have_pet
				aux_wing.pets_allowed = i.pets_allowed
				aux_wing.blankets = i.blankets
				aux_wing.live_center = i.live_center

				for j in i.public_transport.filter():
					if j.name == 'bus':
						aux_wing.bus = True
					if j.name == 'taxi':
						aux_wing.taxi = True
					if j.name == 'train':
						aux_wing.train = True
					if j.name == 'boat':
						aux_wing.boat = True
					if j.name == 'metro':
						aux_wing.metro = True
					if j.name == 'others':
						aux_wing.others = True
					if j.name == 'car':
						aux_wing.car = True
					if j.name == 'plane':
						aux_wing.plane = True
					if j.name == 'motorbike':
						aux_wing.motorbike = True
					if j.name == 'bicycle':
						aux_wing.bicycle = True
				aux_wing.about = i.about
				aux_wing.address = i.address
				aux_wing.number = i.number
				aux_wing.additional_information = i.additional_information
				aux_wing.postal_code = i.postal_code	
				objects.append(aux_wing.jsonable())
			else:

				aux_wing = AccomodationWingNotEditable()
				aux_wing.id = i.pk		
				aux_wing.name = i.name
				aux_wing.status = i.status

				if i.date_start is None:
					aux_wing.date_start = "null"
				else:
					aux_wing.date_start = i.date_end

				if i.date_end is None:
					aux_wing.date_end = "null"
				else:
					aux_wing.date_end = i.date_end

				aux_wing.best_days = i.best_days
				city = {}
				city['lat'] = i.city.lat
				city['lon'] = i.city.lon
				city['name'] = i.city.name
				city['region'] = i.city.region.name
				city['country'] = i.city.region.country.name
				aux_wing.city = city
				aux_wing.sharing_once = i.sharing_once
				aux_wing.capacity = i.capacity

				if not i.preferred_male and not i.preferred_female:
					aux_wing.preferred_gender = 'None'
				elif i.preferred_male and not i.preferred_female:
					aux_wing.preferred_gender = 'Male'
				elif not i.preferred_male and i.preferred_female:
					aux_wing.preferred_gender = 'Female'
				elif i.preferred_male and i.preferred_female:
					aux_wing.preferred_gender = 'Both'

				aux_wing.wheelchair = i.wheelchair
				aux_wing.where_sleeping_type = i.where_sleeping_type
				aux_wing.smoking = i.smoking
				aux_wing.i_have_pet = i.i_have_pet
				aux_wing.pets_allowed = i.pets_allowed
				aux_wing.blankets = i.blankets
				aux_wing.live_center = i.live_center

				for j in i.public_transport.filter():
					if j.name == 'bus':
						aux_wing.bus = True
					if j.name == 'tram':
						aux_wing.tram = True
					if j.name == 'train':
						aux_wing.train = True
					if j.name == 'boat':
						aux_wing.boat = True
					if j.name == 'metro':
						aux_wing.metro = True
					if j.name == 'others':
						aux_wing.others = True
				aux_wing.about = i.about
				objects.append(aux_wing.jsonable())
		return self.create_response(request, {"status":True, "data":objects})
	
	def validate_post(self, POST):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		invalid = {"type":"INVALID", "extras":[]}

		date_start = None
		date_end = None
		"""
		if POST.has_key('XXX'):
			if POST['XXX'] == "":
				not_empty['extras'].append('XXX')
			elif POST['XXX'] not in []:
				invalid['extras'].append('XXX')
		else:
			field_req['extras'].append('XXX')
		"""
		if POST.has_key('taxi'):
			if POST['taxi'] == "":
				not_empty['extras'].append('taxi')
			elif POST['taxi'] not in [True, False]:
				invalid['extras'].append('taxi')
		else:
			field_req['extras'].append('taxi')

		if POST.has_key('bus'):
			if POST['bus'] == "":
				not_empty['extras'].append('bus')
			elif POST['bus'] not in [True, False]:
				invalid['extras'].append('bus')
		else:
			field_req['extras'].append('bus')

		if POST.has_key('metro'):
			if POST['metro'] == "":
				not_empty['extras'].append('metro')
			elif POST['metro'] not in [True, False]:
				invalid['extras'].append('metro')
		else:
			field_req['extras'].append('metro')

		if POST.has_key('train'):
			if POST['train'] == "":
				not_empty['extras'].append('train')
			elif POST['train'] not in [True, False]:
				invalid['extras'].append('train')
		else:
			field_req['extras'].append('train')

		if POST.has_key('other'):
			if POST['other'] == "":
				not_empty['extras'].append('other')
			elif POST['other'] not in [True, False]:
				invalid['extras'].append('other')
		else:
			field_req['extras'].append('other')

		if POST.has_key('boat'):
			if POST['boat'] == "":
				not_empty['extras'].append('boat')
			elif POST['boat'] not in [True, False]:
				invalid['extras'].append('boat')
		else:
			field_req['extras'].append('boat')

		if POST.has_key('plane'):
			if POST['plane'] == "":
				not_empty['extras'].append('plane')
			elif POST['plane'] not in [True, False]:
				invalid['extras'].append('plane')
		else:
			field_req['extras'].append('plane')			

		if POST.has_key('car'):
			if POST['car'] == "":
				not_empty['extras'].append('car')
			elif POST['car'] not in [True, False]:
				invalid['extras'].append('car')
		else:
			field_req['extras'].append('car')

		if POST.has_key('motorbike'):
			if POST['motorbike'] == "":
				not_empty['extras'].append('motorbike')
			elif POST['motorbike'] not in [True, False]:
				invalid['extras'].append('motorbike')
		else:
			field_req['extras'].append('motorbike')

		if POST.has_key('bicycle'):
			if POST['bicycle'] == "":
				not_empty['extras'].append('bicycle')
			elif POST['bicycle'] not in [True, False]:
				invalid['extras'].append('bicycle')
		else:
			field_req['extras'].append('bicycle')

		if POST.has_key('liveCenter'):
			if POST['liveCenter'] == "":
				not_empty['extras'].append('liveCenter')
			elif POST['liveCenter'] not in [True, False]:
				invalid['extras'].append('liveCenter')
		else:
			field_req['extras'].append('liveCenter')

		if POST.has_key('petsAllowed'):
			if POST['petsAllowed'] == "":
				not_empty['extras'].append('petsAllowed')
			elif POST['petsAllowed'] not in [True, False]:
				invalid['extras'].append('petsAllowed')
		else:
			field_req['extras'].append('petsAllowed')

		if POST.has_key('wheelchair'):
			if POST['wheelchair'] == "":
				not_empty['extras'].append('wheelchair')
			elif POST['wheelchair'] not in [True, False]:
				invalid['extras'].append('wheelchair')
		else:
			field_req['extras'].append('wheelchair')

		if POST.has_key('sharingOnce'):
			if POST['sharingOnce'] == "":
				not_empty['extras'].append('sharingOnce')
			elif POST['sharingOnce'] not in [True, False]:
				invalid['extras'].append('sharingOnce')
		else:
			field_req['extras'].append('sharingOnce')

		if POST.has_key('iHavePet'):
			if POST['iHavePet'] == "":
				not_empty['extras'].append('iHavePet')
			elif POST['iHavePet'] not in [True, False]:
				invalid['extras'].append('iHavePet')
		else:
			field_req['extras'].append('iHavePet')

		if POST.has_key('blankets'):
			if POST['blankets'] == "":
				not_empty['extras'].append('blankets')
			elif POST['blankets'] not in [True, False]:
				invalid['extras'].append('blankets')
		else:
			field_req['extras'].append('blankets')

		if POST.has_key('name'):
			if POST['name'] == "":
				not_empty['extras'].append('name')
			elif len(POST['name']) > 100:
				too_long['extras'].append('name')
		else:
			field_req['extras'].append('name')

		if POST.has_key('status'):
			if POST['status'] == "":
				not_empty['extras'].append('status')
			elif POST['status'] not in ['Y', 'M', 'T', 'N', 'C', 'W']:
				invalid['extras'].append('status')
		else:
			field_req['extras'].append('status')

		if POST.has_key('bestDays'):
			if POST['bestDays'] == "":
				not_empty['extras'].append('bestDays')
			elif POST['bestDays'] not in ['A', 'F', 'T', 'W']:
				invalid['extras'].append('bestDays')
		else:
			field_req['extras'].append('bestDays')
		
		if POST.has_key('capacity'):
			if POST['capacity'] == "":
				not_empty['extras'].append('capacity')
			elif int(POST['capacity']) not in range(10):
				invalid['extras'].append('capacity')
		else:
			field_req['extras'].append('capacity')

		if POST.has_key('preferredGender'):
			if POST['preferredGender'] == "":
				not_empty['extras'].append('preferredGender')
			elif POST['preferredGender'] not in ['Male', 'Female', 'Both', 'None']:
				invalid['extras'].append('preferredGender')
		else:
			field_req['extras'].append('preferredGender')

		if POST.has_key('whereSleepingType'):
			if POST['whereSleepingType'] == "":
				not_empty['extras'].append('whereSleepingType')
			elif POST['whereSleepingType'] not in ['C', 'P', 'S']:
				invalid['extras'].append('whereSleepingType')
		else:
			field_req['extras'].append('whereSleepingType')

		if POST.has_key('smoking'):
			if POST['smoking'] == "":
				not_empty['extras'].append('smoking')
			elif POST['smoking'] not in ['S', 'D', 'N']:
				invalid['extras'].append('smoking')
		else:
			field_req['extras'].append('smoking')

		if POST.has_key('about'):
			if len(POST['about']) > 1000:
				too_long['extras'].append('about')
		else:
			field_req['extras'].append('about')

		if POST.has_key('address'):
			if POST['address'] == "":
				not_empty['extras'].append('address')
			elif len(POST['address']) > 500:
				too_long['extras'].append('address')
		else:
			field_req['extras'].append('address')

		if POST.has_key('number'):
			if POST['number'] == "":
				not_empty['extras'].append('number')
			elif len(POST['number']) > 50:
				too_long['extras'].append('number')
		else:
			field_req['extras'].append('number')

		if POST.has_key('additionalInformation'):
			if len(POST['additionalInformation']) > 500:
				too_long['extras'].append('additionalInformation')

		if POST.has_key('postalCode'):
			if POST['postalCode'] == "":
				not_empty['extras'].append('postalCode')
			elif len(POST['postalCode']) > 50:
				too_long['extras'].append('postalCode')
		else:
			field_req['extras'].append('postalCode')

		if POST.has_key('dateStart'):
			if POST.has_key('sharingOnce') and POST['sharingOnce'] is True:
				if POST['dateStart'] == "":
					not_empty['extras'].append('dateStart')
				else:
					#we need to check if date start its a valid date and >= today
					try:
						date_start = datetime.datetime.strptime(POST['dateStart'], '%Y-%m-%d')
						if date_start < date.today():
							invalid['extras'].append('dateStart')
					except:
						invalid['extras'].append('dateStart')					

			else:
				invalid['extras'].append('dateStart')

		if POST.has_key('dateEnd'):
			if POST.has_key('sharingOnce') and POST['sharingOnce'] is True:
				if POST['dateEnd'] == "":
					not_empty['extras'].append('dateEnd')
				else:
					#we need to check if date start its a valid date and >= today
					try:
						date_end = datetime.datetime.strptime(POST['dateEnd'], '%Y-%m-%d')
						if date_end < date.today():
							invalid['extras'].append('dateEnd')
					except:
						invalid['extras'].append('dateEnd')					

			else:
				invalid['extras'].append('dateEnd')

		if date_start is not None and date_end is not None and date_start > date_end:
			invalid['extras'].append('dates')

		if POST.has_key('city'):
			if not isinstance(POST['city'], dict):
				invalid['extras'].append('city')
			else:
				if POST['city'] == {}:
					not_empty['extras'].append('city')
				elif not POST['city'].has_key('lat') and POST['city'].has_key('lon') and POST['city'].has_key('country') and POST['city'].has_key('name'):
					invalid['extras'].append('city')
		else:
			field_req['extras'].append('city')


		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(too_long['extras']) > 0:
			errors.append(too_long)
		if len(invalid['extras']) > 0:
			errors.append(invalid)

		return errors

	def build_transports(self, POST):
		#Metro, Bus, Taxi, Train, Car, Motorbike, Bicycle, Boat, Plane, Other
		transports = []
		if POST['metro'] is True:
			transports.append(PublicTransport.objects.get(name='metro'))

		if POST['bus'] is True:
			transports.append(PublicTransport.objects.get(name='bus'))

		if POST['taxi'] is True:
			transports.append(PublicTransport.objects.get(name='taxi'))

		if POST['train'] is True:
			transports.append(PublicTransport.objects.get(name='train'))
		
		if POST['car'] is True:
			transports.append(PublicTransport.objects.get(name='car'))
		
		if POST['motorbike'] is True:
			transports.append(PublicTransport.objects.get(name='motorbike'))

		if POST['bicycle'] is True:
			transports.append(PublicTransport.objects.get(name='bicycle'))

		if POST['boat'] is True:
			transports.append(PublicTransport.objects.get(name='boat'))

		if POST['plane'] is True:
			transports.append(PublicTransport.objects.get(name='plane'))

		if POST['other'] is True:
			transports.append(PublicTransport.objects.get(name='other'))
												
		return transports
		
	def post_list(self, request, **kwargs):		
		POST = json.loads(request.raw_post_data)	
		try:
			prof = UserProfile.objects.get(user=request.user)
		except:
			return self.create_response(request, {"status" : False, "errors": [{"type": "INTERNAL_ERROR"}]}, response_class=HttpResponse)

		if kwargs.has_key('profile_id'):
			target_prof = kwargs['profile_id']
		else:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["profile"]}]}, response_class=HttpResponse)

		if prof.pk != int(target_prof):
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		#Now we are sure that the user wants to do a correct action...
		errors = self.validate_post(json.loads(request.raw_post_data))
		if len(errors) > 0:
			return self.create_response(request, {"status" : False, "errors": errors}, response_class=HttpResponse)
		#import pdb; pdb.set_trace()
		city = City.objects.saveLocation(country=POST['city']['country'], region=POST['city']['region'], lat=POST['city']['lat'], lon=POST['city']['lon'], name=POST['city']['name'])
		transport = self.build_transports(POST)

		if 'Both' in POST['preferredGender']:
			pref_male = True
			pref_female = True
		elif 'Male' in POST['preferredGender']:
			pref_male = True
			pref_female = False
		elif 'Female' in POST['preferredGender']:
			pref_male = False
			pref_female = True
		elif 'None' in POST['preferredGender']:
			pref_male = False
			pref_female = False

		if not POST.has_key('additionalInformation'): POST['additionalInformation'] = ""
		if not POST.has_key('about'): POST['about'] = ""
		#∫import pdb; pdb.set_trace()
		acc= Accomodation.objects.create(author=prof, name=POST['name'], status=POST['status'], date_start=getattr(POST, 'dateStart', None), date_end=getattr(POST, 'dateEnd', None), best_days=POST['bestDays'], is_request=False, city=city, active=True, sharing_once=POST['sharingOnce'], capacity=POST['capacity'], preferred_male=pref_male, preferred_female=pref_female, wheelchair=POST['wheelchair'], where_sleeping_type=POST['whereSleepingType'], smoking=POST['smoking'], i_have_pet=POST['iHavePet'], pets_allowed=POST['petsAllowed'], blankets=POST['blankets'], live_center=POST['liveCenter'], about=POST['about'], address=POST['address'], number=POST['number'], additional_information=POST['additionalInformation'], postal_code=POST['postalCode'])
		for i in transport:
			acc.public_transport.add(i)
		acc.save()
		return self.create_response(request, {"status":True})

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

	def put_detail(self, request, **kwargs):		
		#import pdb; pdb.set_trace()
		PUT = json.loads(request.raw_post_data)	
		try:
			prof = UserProfile.objects.get(user=request.user)
		except:
			return self.create_response(request, {"status" : False, "errors": [{"type": "INTERNAL_ERROR"}]}, response_class=HttpResponse)

		if kwargs.has_key('profile_id'):
			target_prof = kwargs['profile_id']
		else:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["profile"]}]}, response_class=HttpResponse)

		if kwargs.has_key('wing_id'):
			target_wing = kwargs['wing_id']
		else:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["wing"]}]}, response_class=HttpResponse)

		try:
			acc = Accomodation.objects.get(pk=target_wing)
		except:
			return self.create_response(request, {"status" : False, "errors": [{"type": "INTERNAL_ERROR"}]}, response_class=HttpResponse)

		if prof.pk != int(target_prof):
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)

		if acc.author.pk != prof.pk:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)

		#Now we are sure that the user wants to do a correct action...
		errors = self.validate_post(json.loads(request.raw_post_data))
		if len(errors) > 0:
			return self.create_response(request, {"status" : False, "errors": errors}, response_class=HttpResponse)
		
		if not PUT['city'].has_key('region'):
			PUT['city']['region'] = 'No region'
		city = City.objects.saveLocation(country=PUT['city']['country'], region=PUT['city']['region'], lat=PUT['city']['lat'], lon=PUT['city']['lon'], name=PUT['city']['name'])
		transport = self.build_transports(PUT)
		pref_male = 'Male' in PUT['preferredGender']
		pref_female= 'Female' in PUT['preferredGender']
		if not PUT.has_key('additionalInformation'): PUT['additionalInformation'] = ""
		if not PUT.has_key('about'): PUT['about'] = ""

		acc.name=PUT['name'] 
		acc.status=PUT['status'] 
		acc.date_start=getattr(PUT, 'dateStart', None) 
		acc.date_end=getattr(PUT, 'dateEnd', None)
		acc.best_days=PUT['bestDays']
		acc.is_request=False
		acc.city=city
		acc.active=True
		acc.sharing_once=PUT['sharingOnce']
		acc.capacity=PUT['capacity']
		acc.preferred_male=pref_male
		acc.preferred_female=pref_female
		acc.wheelchair=PUT['wheelchair']
		acc.where_sleeping_type=PUT['whereSleepingType']
		acc.smoking=PUT['smoking']
		acc.i_have_pet=PUT['iHavePet']
		acc.pets_allowed=PUT['petsAllowed']
		acc.blankets=PUT['blankets']
		acc.live_center=PUT['liveCenter']
		acc.about=PUT['about']
		acc.address=PUT['address']
		acc.number=PUT['number']
		acc.additional_information=PUT['additionalInformation']
		acc.postal_code=PUT['postalCode']
		acc.public_transport.clear()
		for i in transport:
			acc.public_transport.add(i)
		acc.save()
		return self.create_response(request, {"status":True})

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
	
