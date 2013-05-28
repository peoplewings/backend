
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
		detail_allowed_methods = ['put', 'delete']
		list_allowed_methods = ['get', 'post']
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		include_resource_uri = False
		resource_name='wings'

	def get_list(self, request, **kwargs):
		#Check authentication	
		#print kwargs		
		data = None			
		if str(request.user.pk) == str(kwargs['profile_id']):
			#We have to list our own wings
			data = []
			wings = Wing.objects.filter(author__pk=str(kwargs['profile_id']))			
			for w in wings:
				wing_obj = self.get_generic_fields(w)				
				if w.wing_type == 'Accomodation':
					wing_obj.extraFields= self.get_own_accomodation_fields(w.pk)
				if w.wing_type == 'Meetup':
					pass
					#wing_obj.extraFields = self.get_own_meetup_fields(w.pk)
				data.append(wing_obj)

		else:
			#We have to list another user wings
			data = []
			wings = Wing.objects.filter(author__pk=str(kwargs['profile_id']))
			for w in wings:
				wing_obj = self.get_generic_fields(w)
				if w.wing_type == 'Accomodation':
					wing_obj.extraFields= self.get_other_accomodation_fields(w.pk)
				data.append(wing_obj)

		if data is not None:
			return self.create_response(request, {"status" : True, "data": [i.jsonable() for i in data]}, response_class=HttpResponse)
		else:
			return self.create_response(request, {"status" : False, "errors": [{"type": "INTERNAL_ERROR"}]}, response_class=HttpResponse)

	def get_generic_fields(self, w):
		wing_obj = WingObj()
		wing_obj.idWing = w.pk
		wing_obj.author = w.author.pk
		wing_obj.name = w.name
		wing_obj.status = w.status
		wing_obj.wing_type = w.wing_type
		wing_obj.dateStart = w.date_start
		wing_obj.dateEnd = w.date_end
		wing_obj.bestDays = w.best_days
		wing_obj.city = w.city.jsonify()
		return wing_obj

	def get_own_accomodation_fields(self, id_wing):		
		fields = []
		#import pdb; pdb.set_trace()
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
		fields.append({'number': acc.number})
		fields.append({'additionalInformation': acc.additional_information})
		fields.append({'postalCode': acc.postal_code})

		fields.append({'PublicTransport': [i.name for i in acc.public_transport.all()]})
		if acc.preferred_female is True and acc.preferred_male is True:
			fields.append({'preferredGender': 'Both'})
		elif acc.preferred_male is True:
			fields.append({'preferredGender': 'Male'})
		else:
			fields.append({'preferredGender': 'Female'})
		return fields

	def get_other_accomodation_fields(self, id_wing):
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

		fields.append({'publicTransports': [i.name for i in acc.public_transport.all()]})
		if acc.preferred_female is True and acc.preferred_male is True:
			fields.append({'preferredGender': 'Both'})
		elif acc.preferred_male is True:
			fields.append({'preferredGender': 'Male'})
		else:
			fields.append({'preferredGender': 'Female'})
		return fields

	def construct_generic_post_params(self, request, POST):
		result = {}
		result['name'] = POST['name']
		result['author'] = UserProfile.objects.get(user=request.user)
		result['status'] = POST['status']
		if (POST.has_key('dateStart')):
			result['date_start'] = datetime.datetime.strptime(POST['dateStart'], '%Y-%m-%d')
		if (POST.has_key('dateEnd')):
			result['date_end'] = datetime.datetime.strptime(POST['dateEnd'], '%Y-%m-%d')
		result['best_days'] = POST['bestDays']
		result['is_request'] = True
		result['city']= City.objects.saveLocation(**POST['city'])
		result['active'] = True
		result['wing_type'] = POST['type']
		return result

	def construct_accomodation_post_params(self, params, POST):
		if POST.has_key('sharingOnce'):
			params['sharing_once'] = POST['sharingOnce']
		if POST.has_key('capacity'):
			params['capacity'] = POST['capacity']
		if POST.has_key('preferredGender'):
			params['preferred_male'] = POST['preferredGender'] in ['Both', 'Male']
		if POST.has_key('preferredGender'):
			params['preferred_female'] = POST['preferredGender'] in ['Both', 'Female']
		if POST.has_key('wheelchair'):
			params['wheelchair'] = POST['wheelchair']
		if POST.has_key('whereSleepingType'):
			params['where_sleeping_type'] = POST['whereSleepingType']
		if POST.has_key('smoking'):
			params['smoking'] = POST['smoking']
		if POST.has_key('iHavePet'):
			params['i_have_pet'] = POST['iHavePet']
		if POST.has_key('petsAllowed'):
			params['pets_allowed'] = POST['petsAllowed']
		if POST.has_key('blankets'):
			params['blankets'] = POST['blankets']
		if POST.has_key('liveCenter'):
			params['live_center'] = POST['liveCenter']
		if POST.has_key('about'):
			params['about'] = POST['about']
		if POST.has_key('address'):
			params['address'] = POST['address']
		if POST.has_key('number'):
			params['number'] = POST['number']
		if POST.has_key('additionalInformation'):
			params['additional_information'] = POST['additionalInformation']
		if POST.has_key('postalCode'):
			params['postal_code'] = POST['postalCode']
		return params

	def validate_POST(self, POST):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		invalid = {"type":"INVALID", "extras":[]}

		date_start = None
		date_end = None

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

		if POST.has_key('type'):
			if POST['type'] not in ['Accomodation']:
				invalid['extras'].append('type')
			else:
				if POST['type'] == 'Accomodation':
					#Validate Accomodation specific fields					
					if POST.has_key('liveCenter'):
						if POST['liveCenter'] == "":
							not_empty['extras'].append('liveCenter')
						elif POST['liveCenter'] not in [True, False]:
							invalid['extras'].append('liveCenter')

					if POST.has_key('petsAllowed'):
						if POST['petsAllowed'] == "":
							not_empty['extras'].append('petsAllowed')
						elif POST['petsAllowed'] not in [True, False]:
							invalid['extras'].append('petsAllowed')

					if POST.has_key('wheelchair'):
						if POST['wheelchair'] == "":
							not_empty['extras'].append('wheelchair')
						elif POST['wheelchair'] not in [True, False]:
							invalid['extras'].append('wheelchair')

					if POST.has_key('sharingOnce'):
						if POST['sharingOnce'] == "":
							not_empty['extras'].append('sharingOnce')
						elif POST['sharingOnce'] not in [True, False]:
							invalid['extras'].append('sharingOnce')

					if POST.has_key('iHavePet'):
						if POST['iHavePet'] == "":
							not_empty['extras'].append('iHavePet')
						elif POST['iHavePet'] not in [True, False]:
							invalid['extras'].append('iHavePet')

					if POST.has_key('blankets'):
						if POST['blankets'] == "":
							not_empty['extras'].append('blankets')
						elif POST['blankets'] not in [True, False]:
							invalid['extras'].append('blankets')
					
					if POST.has_key('capacity'):
						if POST['capacity'] == "":
							not_empty['extras'].append('capacity')
						elif int(POST['capacity']) not in range(10):
							invalid['extras'].append('capacity')

					if POST.has_key('preferredGender'):
						if POST['preferredGender'] == "":
							not_empty['extras'].append('preferredGender')
						elif POST['preferredGender'] not in ['Male', 'Female', 'Both', 'None']:
							invalid['extras'].append('preferredGender')

					if POST.has_key('whereSleepingType'):
						if POST['whereSleepingType'] == "":
							not_empty['extras'].append('whereSleepingType')
						elif POST['whereSleepingType'] not in ['C', 'P', 'S']:
							invalid['extras'].append('whereSleepingType')

					if POST.has_key('smoking'):
						if POST['smoking'] == "":
							not_empty['extras'].append('smoking')
						elif POST['smoking'] not in ['S', 'D', 'N']:
							invalid['extras'].append('smoking')

					if POST.has_key('about'):
						if len(POST['about']) > 1000:
							too_long['extras'].append('about')

					if POST.has_key('address'):
						if POST['address'] == "":
							not_empty['extras'].append('address')
						elif len(POST['address']) > 500:
							too_long['extras'].append('address')

					if POST.has_key('number'):
						if POST['number'] == "":
							not_empty['extras'].append('number')
						elif len(POST['number']) > 50:
							too_long['extras'].append('number')

					if POST.has_key('additionalInformation'):
						if len(POST['additionalInformation']) > 500:
							too_long['extras'].append('additionalInformation')

					if POST.has_key('postalCode'):
						if POST['postalCode'] == "":
							not_empty['extras'].append('postalCode')
						elif len(POST['postalCode']) > 50:
							too_long['extras'].append('postalCode')
		else:
			field_req['extras'].append('type')

		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(too_long['extras']) > 0:
			errors.append(too_long)
		if len(invalid['extras']) > 0:
			errors.append(invalid)

		return errors

	def post_list(self, request, **kwargs):
		#Check if kwargs['profile_id'] == request.user.pk		
		if str(request.user.pk) != str(kwargs['profile_id']):
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)

		POST = json.loads(request.raw_post_data)
		errors = []
		errors = self.validate_POST(POST)
		if len(errors) != 0:
			return self.create_response(request, {"status" : False, "errors": errors}, response_class=HttpResponse)	
		
		#Create the wing, and also create the wing_type
		params = self.construct_generic_post_params(request, POST)
		if (POST['type'] == 'Accomodation'):
			params = self.construct_accomodation_post_params(params, POST)
			acc = Accomodation.objects.create(**params)
			import pdb; pdb.set_trace()
			if POST.has_key('publicTransports'):
				for i in POST['publicTransports']:
					if len(PublicTransport.objects.filter(name=i)) == 1:
						acc.public_transport.add(PublicTransport.objects.get(name=i))
				acc.save()

		return self.create_response(request, {"status" : True}, response_class=HttpResponse)

	def validate_PUT(self, PUT):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		invalid = {"type":"INVALID", "extras":[]}

		date_start = None
		date_end = None

		if PUT.has_key('name'):
			if PUT['name'] == "":
				not_empty['extras'].append('name')
			elif len(PUT['name']) > 100:
				too_long['extras'].append('name')
		else:
			field_req['extras'].append('name')

		if PUT.has_key('status'):
			if PUT['status'] == "":
				not_empty['extras'].append('status')
			elif PUT['status'] not in ['Y', 'M', 'T', 'N', 'C', 'W']:
				invalid['extras'].append('status')
		else:
			field_req['extras'].append('status')

		if PUT.has_key('bestDays'):
			if PUT['bestDays'] == "":
				not_empty['extras'].append('bestDays')
			elif PUT['bestDays'] not in ['A', 'F', 'T', 'W']:
				invalid['extras'].append('bestDays')
		else:
			field_req['extras'].append('bestDays')

		if PUT.has_key('dateStart'):
			if PUT.has_key('sharingOnce') and PUT['sharingOnce'] is True:
				if PUT['dateStart'] == "":
					not_empty['extras'].append('dateStart')
				else:
					#we need to check if date start its a valid date and >= today
					try:
						date_start = datetime.datetime.strptime(PUT['dateStart'], '%Y-%m-%d')
						if date_start < date.today():
							invalid['extras'].append('dateStart')
					except:
						invalid['extras'].append('dateStart')					

			else:
				invalid['extras'].append('dateStart')

		if PUT.has_key('dateEnd'):
			if PUT.has_key('sharingOnce') and PUT['sharingOnce'] is True:
				if PUT['dateEnd'] == "":
					not_empty['extras'].append('dateEnd')
				else:
					#we need to check if date start its a valid date and >= today
					try:
						date_end = datetime.datetime.strptime(PUT['dateEnd'], '%Y-%m-%d')
						if date_end < date.today():
							invalid['extras'].append('dateEnd')
					except:
						invalid['extras'].append('dateEnd')					

			else:
				invalid['extras'].append('dateEnd')

		if date_start is not None and date_end is not None and date_start > date_end:
			invalid['extras'].append('dates')

		if PUT.has_key('city'):
			if not isinstance(PUT['city'], dict):
				invalid['extras'].append('city')
			else:
				if PUT['city'] == {}:
					not_empty['extras'].append('city')
				elif not PUT['city'].has_key('lat') and PUT['city'].has_key('lon') and PUT['city'].has_key('country') and PUT['city'].has_key('name'):
					invalid['extras'].append('city')
		else:
			field_req['extras'].append('city')

		if PUT.has_key('type'):
			if PUT['type'] not in ['Accomodation']:
				invalid['extras'].append('type')
			else:
				if PUT['type'] == 'Accomodation':
					#Validate Accomodation specific fields
					if PUT.has_key('liveCenter'):
						if PUT['liveCenter'] not in [True, False]:
							invalid['extras'].append('liveCenter')

					if PUT.has_key('petsAllowed'):
						if PUT['petsAllowed'] not in [True, False]:
							invalid['extras'].append('petsAllowed')

					if PUT.has_key('wheelchair'):
						if PUT['wheelchair'] not in [True, False]:
							invalid['extras'].append('wheelchair')

					if PUT.has_key('sharingOnce'):
						if PUT['sharingOnce'] not in [True, False]:
							invalid['extras'].append('sharingOnce')

					if PUT.has_key('iHavePet'):
						if PUT['iHavePet'] not in [True, False]:
							invalid['extras'].append('iHavePet')

					if PUT.has_key('blankets'):
						if PUT['blankets'] not in [True, False]:
							invalid['extras'].append('blankets')
					
					if PUT.has_key('capacity'):
						if int(PUT['capacity']) not in range(10):
							invalid['extras'].append('capacity')

					if PUT.has_key('preferredGender'):
						if PUT['preferredGender'] not in ['Male', 'Female', 'Both', 'None']:
							invalid['extras'].append('preferredGender')

					if PUT.has_key('whereSleepingType'):
						if PUT['whereSleepingType'] not in ['C', 'P', 'S']:
							invalid['extras'].append('whereSleepingType')

					if PUT.has_key('smoking'):
						if PUT['smoking'] not in ['S', 'D', 'N']:
							invalid['extras'].append('smoking')

					if PUT.has_key('about'):
						if len(PUT['about']) > 1000:
							too_long['extras'].append('about')

					if PUT.has_key('address'):
						if PUT['address'] == "":
							not_empty['extras'].append('address')
						elif len(PUT['address']) > 500:
							too_long['extras'].append('address')

					if PUT.has_key('number'):
						if PUT['number'] == "":
							not_empty['extras'].append('number')
						elif len(PUT['number']) > 50:
							too_long['extras'].append('number')

					if PUT.has_key('additionalInformation'):
						if len(PUT['additionalInformation']) > 500:
							too_long['extras'].append('additionalInformation')

					if PUT.has_key('postalCode'):
						if PUT['postalCode'] == "":
							not_empty['extras'].append('postalCode')
						elif len(PUT['postalCode']) > 50:
							too_long['extras'].append('postalCode')
		else:
			field_req['extras'].append('type')

		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(too_long['extras']) > 0:
			errors.append(too_long)
		if len(invalid['extras']) > 0:
			errors.append(invalid)

		return errors

	def update_generic(self, PUT, wing):
		wing.name = PUT['name']
		wing.status = PUT['status']
		wing.best_days = PUT['bestDays']
		wing.city = City.objects.saveLocation(**PUT['city'])

		if PUT.has_key('dateStart'):
			wing.date_start = datetime.datetime.strptime(PUT['dateStart'], '%Y-%m-%d')
		else:
			wing.date_start = None
		if PUT.has_key('dateEnd'):
			wing.end_date = datetime.datetime.strptime(PUT['dateEnd'], '%Y-%m-%d')
		else:
			wing.end_date = None
		wing.save()

	def update_accomodation(self, PUT, w):
		wing = Accomodation.objects.get(pk=w.pk)
		if PUT.has_key('sharingOnce') and PUT['sharingOnce'] is True:
			wing.sharing_once = True
		else: wing.sharing_once = False

		if PUT.has_key('capacity'):
			wing.capacity = PUT['capacity']

		if PUT.has_key('preferredGender'):
			if PUT['preferredGender'] == 'Both':
				wing.preferred_female = True
				wing.preferred_male = True
			elif PUT['preferredGender'] == 'Male':
				wing.preferred_male = True
			elif PUT['preferredGender'] == 'Female':
				wing.preferred_female = True
		else: 
			wing.preferred_female = False
			wing.preferred_male = False

		if PUT.has_key('wheelchair') and PUT['wheelchair'] is True:
			wing.wheelchair = True
		else: wing.wheelchair = False

		if PUT.has_key('whereSleepingType'):
			wing.where_sleeping_type = PUT['whereSleepingType']
		
		if PUT.has_key('smoking'):
			wing.smoking = PUT['smoking']

		if PUT.has_key('iHavePet') and PUT['iHavePet'] is True:
			wing.i_have_pet = True
		else: wing.i_have_pet = False

		if PUT.has_key('petsAllowed') and PUT['petsAllowed'] is True:
			wing.pets_allowed = True
		else: wing.pets_allowed = False

		if PUT.has_key('blankets') and PUT['blankets'] is True:
			wing.blankets = True
		else: wing.blankets = False

		if PUT.has_key('liveCenter') and PUT['liveCenter'] is True:
			wing.live_center = True
		else: wing.live_center = False

		if PUT.has_key('publicTransports'):
			#import pdb; pdb.set_trace()
			wing.public_transport.clear()
			for pb in PUT['publicTransports']:
				aux = PublicTransport.objects.filter(name=pb)
				if len(aux) == 1: wing.public_transport.add(aux[0])
		else: wing.public_transport.clear()

		if PUT.has_key('about'):
			wing.about = PUT['about']
		else: wing.about = ""

		if PUT.has_key('address'):
			wing.address = PUT['address']
		else: wing.address = ""

		if PUT.has_key('number'):
			wing.number = PUT['number']
		else: wing.number = ""

		if PUT.has_key('additionalInformation'):
			wing.additional_information = PUT['additionalInformation']
		else: wing.additional_information = ""

		if PUT.has_key('postalCode'):
			wing.postal_code = PUT['postalCode']
		else: wing.postal_code = ""

		wing.save()


	def put_detail(self, request, **kwargs):		
		import pdb; pdb.set_trace()
		if str(request.user.pk) != str(kwargs['profile_id']):
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		w_list = Wing.objects.filter(pk=str(kwargs['wing_id']), author=UserProfile.objects.get(user=request.user))
		if len(w_list) != 1:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		wing = w_list[0]

		PUT = json.loads(request.raw_post_data)
		errors = []
		errors = self.validate_PUT(PUT)
		if len(errors) != 0:
			return self.create_response(request, {"status" : False, "errors": errors}, response_class=HttpResponse)

		self.update_generic(PUT, wing)
		if PUT['type'] == 'Accomodation':
			self.update_accomodation(PUT, wing)

		return self.create_response(request, {"status" : True}, response_class=HttpResponse)

	def delete_detail(self, request, **kwargs):
		if str(request.user.pk) != str(kwargs['profile_id']):
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		w_list = Wing.objects.filter(pk=str(kwargs['wing_id']), author=UserProfile.objects.get(user=request.user))
		if len(w_list) != 1:
			return self.create_response(request, {"status" : False, "errors": [{"type": "FORBIDDEN"}]}, response_class=HttpResponse)
		wing = w_list[0]

		wtype = wing.wing_type
		if wtype == 'Accomodation':
			awing = Accomodation.objects.get(pk=wing.pk)
			awing.delete()

		wing.delete()
		return self.create_response(request, {"status" : True}, response_class=HttpResponse)