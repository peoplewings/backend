
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
	class Meta:
		object_class = Wing
		queryset = Wing.objects.all()
		detail_allowed_methods = ['get', 'post', 'put']
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		include_resource_uri = False
		resource_name='wings'

	def get_list(self, request, **kwargs):
		#Check authentication	
		data = None	
		if request.has_key('user') and request.user.pk == kwargs['id_user']:
			#We have to list our own wings
			data = []
			wings = Wing.objects.filter(author__pk=kwargs['id_user'])
			for w in wings:
				wing_obj = WingObj()
				wing_obj.idWing = w.pk
				wing_obj.author = w.author.pk
				wing_obj.name = w.name
				wing_obj.status = w.status
				wing_obj.type = w.type
				wing_obj.dateStart = w.date_start
				wing_obj.dateEnd = w.date_end
				wing_obj.bestDays = w.best_days
				wing_obj.city = w.city.jsonify()
				if w.type == 'Accomodation':
					wing_obj.extraFields= self.get_own_accomodation_fields(w.pk)
				data.append(w)

		elif request.has_key('user'):
			#We have to list another user wings
			data = []
			wings = Wing.objects.filter(author__pk=kwargs['id_user'])
			for w in wings:
				wing_obj = WingObj()
				wing_obj.idWing = w.pk
				wing_obj.author = w.author.pk
				wing_obj.name = w.name
				wing_obj.status = w.status
				wing_obj.type = w.type
				wing_obj.dateStart = w.date_start
				wing_obj.dateEnd = w.date_end
				wing_obj.bestDays = w.best_days
				wing_obj.city = w.city.jsonify()
				if w.type == 'Accomodation':
					wing_obj.extraFields= self.get_other_accomodation_fields(w.pk)
				data.append(w)
		else:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FIELD_REQUIRED", "extras": ["user"]}]}, response_class=HttpResponse)

		if data is not None:
			return self.create_response(request, {"status" : True, "data": [i.jsonable() for i in data]}, response_class=HttpResponse)
		else:
			return self.create_response(request, {"status" : False, "errors": [{"type": "INTERNAL_ERROR"}]}, response_class=HttpResponse)

	def get_own_accomodation_fields(id_wing):
		fields = []
		acc = Accomodation.objects.get(pk=id_wing)
		fields.append({'sharingOnce': acc.sharing_once})
		fields.append({'capacity': acc.capacity})
		fields.append({'wheelchair': acc.wheelchair})
		fields.append({'whereSleepingType': acc.where_sleeping_type})
		fields.append({'smoking': acc.smoking})
		fields.append({'iHavePet':acc.i_have_pet})
		fields.append({'petsAllowed': acc.pets_allowed})
		fields.append({'blankets': acc.blankets})
		fields.append({'liveCenter': acc.live_center})		
		fields.append({'about': acc.about})

		fields.append({'address':acc.address})
		fields.append({'number', acc.number})
		fields.append({'additionalInformation', acc.additional_information})
		fields.append({'postalCode': acc.postal_code})

		fields.append({'PublicTransport': [i.name for i in acc.public_transport.all()]})
		if acc.preferred_female is True and acc.preferred_male is True:
			fields.append({'preferredGender': 'Both'})
		elif acc.preferred_male is True:
			fields.append({'preferredGender': 'Male'})
		else:
			fields.append({'preferredGender': 'Female'})

	def get_other_accomodation_fields(id_wing):
		fields = []
		acc = Accomodation.objects.get(pk=id_wing)
		fields.append({'sharingOnce': acc.sharing_once})
		fields.append({'capacity': acc.capacity})
		fields.append({'wheelchair': acc.wheelchair})
		fields.append({'whereSleepingType': acc.where_sleeping_type})
		fields.append({'smoking': acc.smoking})
		fields.append({'iHavePet':acc.i_have_pet})
		fields.append({'petsAllowed': acc.pets_allowed})
		fields.append({'blankets': acc.blankets})
		fields.append({'liveCenter': acc.live_center})		
		fields.append({'about': acc.about})

		fields.append({'PublicTransport': [i.name for i in acc.public_transport.all()]})
		if acc.preferred_female is True and acc.preferred_male is True:
			fields.append({'preferredGender': 'Both'})
		elif acc.preferred_male is True:
			fields.append({'preferredGender': 'Male'})
		else:
			fields.append({'preferredGender': 'Female'})

	def post_list(self, request, **kwargs):
		pass
		


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

	def get_list(self, request, **kwargs):	
		obj = {
			"about": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibu",
			"additionalInformation": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibu",
			"metro": True,
			"bus": True,
			"taxi": True,
			"train": True,
			"car": True,
			"motorbike": True,
			"bicycle": True,
			"boat": True,
			"plane": True,
			"other": True,
			"liveCenter": True,
			"petsAllowed": True,
			"wheelchair": True,
			"sharingOnce": True,
			"iHavePet": True,
			"blankets": True,
			"name": "My Palace",
			"status": "Y",
			"bestDays": "A",
			"capacity": "1",
			"preferredGender": "Male",
			"whereSleepingType": "C",
			"smoking": "N",
			"address": "Carrer Valnecia",
			"number": "430",
			"city": {
			"country": "Germany",
			"name": "Berlin",
			"lon": "13.406091200",
			"lat": "52.519171000",
			"region": "Berlin"
			},
			"postalCode": "1212"
			}	
		return self.create_response(request, {"status":True, "data":obj})
	
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
	
