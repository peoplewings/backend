#People API
import json
import re
import copy
import time
from datetime import date, datetime
from dateutil import parser
from pprint import pprint
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpAccepted, HttpForbidden, HttpApplicationError, HttpApplicationError, HttpMethodNotAllowed, HttpResponse
from tastypie.utils import dict_strip_unicode_keys, trailing_slash
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.forms import ValidationError
from django import forms
from django.utils.cache import patch_cache_control
from django.core import serializers
from django.http import HttpResponse, Http404
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, InvalidPage

from peoplewings.apps.people.models import UserProfile, UserLanguage, Language, University, SocialNetwork, UserSocialNetwork, InstantMessage, UserInstantMessage, UserProfileStudiedUniversity, Interests, References, Photos, PhotoAlbums
from people.domain import *
from peoplewings.global_vars import *
from peoplewings.apps.people.exceptions import *
from peoplewings.apps.ajax.utils import json_response, CamelCaseJSONSerializer
from peoplewings.apps.registration.api import AccountResource
from peoplewings.apps.registration.authentication import ApiTokenAuthentication, AnonymousApiTokenAuthentication
from peoplewings.apps.locations.api import CityResource
from peoplewings.apps.locations.models import Country, Region, City
from peoplewings.apps.wings.api import WingResource
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.apps.wings.models import Accomodation, PublicRequestWing, Wing
from django.contrib.auth.models import User
from peoplewings.apps.registration.views import blitline_token_is_authenticated

class UniversityResource(ModelResource):
	class Meta:
		object_class = University
		queryset = University.objects.all()
		list_allowed_methods = ['get']
		detail_allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		resource_name = "universities"

	def validate(self, GET):
		errors = []
		field_req = {"type": "FIELD_REQUIRED", "extras":[]}
		if not GET.has_key('name'):
			field_req['extras'].append('name')
		if len(field_req['extras']) > 0:
			errors.append(field_req)
		return errors

	def get_list(self, request, **kwargs):
		GET = {}
		for k, v in request.GET.items():
			GET[k]=v
		errors = self.validate(GET)
		if len(errors) > 0: return self.create_response(request, {"status":False, "errors": errors}, response_class=HttpResponse)
		data = []
		qset = Q(name__icontains=GET['name'])
		try:
			result = University.objects.filter(qset)[:5]

			for uni in result:
				data.append({"name": uni.name})
			if len(GET['name']) == 0: data = []
		except Exception, e:
				field_req = {"type": "INTERNAL_ERROR", "extras":[]}
		return self.create_response(request, {"status":True, "data": data}, response_class=HttpResponse)

class ReferencesResource(ModelResource):
	class Meta:
		object_class = References
		queryset = References.objects.all()
		list_allowed_methods = ['post']
		detail_allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		resource_name = "references"

	def validate_POST(self, POST, user):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		invalid = {"type":"INVALID", "extras":[]}

		if not POST.has_key('receiver'):
			field_req['extras'].append('receiver')
		elif POST['receiver'] == user.pk or UserProfile.objects.filter(pk = POST['receiver']).count() == 0:
			invalid['extras'].append('receiver')

		if not POST.has_key('rating'):
			field_req['extras'].append('rating')
		elif POST['rating'] not in ['good', 'neutral', 'bad']:
			invalid['extras'].append('rating')

		if not POST.has_key('metInPerson'):
			field_req['extras'].append('metInPerson')
		elif not isinstance(POST['metInPerson'], bool):
			invalid['extras'].append('metInPerson')

		if not POST.has_key('text'):
			field_req['extras'].append('text')
		elif not isinstance(POST['text'], unicode):
			invalid['extras'].append('text')
		elif len(POST['text']) == 0:
			not_empty['extras'].append('text')
		elif len(POST['text']) > 1000:
			too_long['extras'].append('text')

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
		POST = json.loads(request.raw_post_data)
		#Validate POST data....
		errors = self.validate_POST(POST, request.user)
		if len(errors) > 0: return self.create_response(request, {"status":False, "errors": errors}, response_class=HttpResponse)
		if References.objects.filter(sender=UserProfile.objects.get(user = request.user), receiver = UserProfile.objects.get(pk = POST['receiver'])).count():
			return self.create_response(request, {"status":False, "errors":[{"type":"DUPLICATED_REFERENCE"}]}, response_class = HttpResponse)
		References.objects.create(sender=UserProfile.objects.get(user = request.user), receiver = UserProfile.objects.get(pk = POST['receiver']), rating = POST['rating'], met_in_person = POST['metInPerson'], text = POST['text'])
		return self.create_response(request, {"status":True}, response_class = HttpResponse)

class GeoLocationResource(ModelResource):
	class Meta:
		object_class = UserProfile
		queryset = UserProfile.objects.all()
		list_allowed_methods = ['put']
		detail_allowed_methods = []
		include_resource_uri = False
		always_return_data = True
		resource_name = 'geolocation'
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()

	def validate_PUT(self, PUT):
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		invalid = {"type":"INVALID", "extras":[]}

		if not PUT.has_key('city'):
			field_req['extras'].append('city')

		if not PUT.has_key('country'):
			field_req['extras'].append('country')

		if not PUT.has_key('lat'):
			field_req['extras'].append('lat')

		if not PUT.has_key('lon'):
			field_req['extras'].append('lon')

		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(too_long['extras']) > 0:
			errors.append(too_long)
		if len(invalid['extras']) > 0:
			errors.append(invalid)

		return errors

	def put_list(self, request, **kwargs):
		PUT = json.loads(request.raw_post_data)
		#Validate PUT data....
		errors = self.validate_PUT(PUT)
		if len(errors) > 0: return self.create_response(request, {"status":False, "errors": errors}, response_class=HttpResponse)

		now_city = City.objects.saveLocation(name = PUT['city'], country = PUT['country'], lat = PUT['lat'], lon = PUT['lon'])
		profile = UserProfile.objects.get(user = request.user)
		#Si no tiene current city le assignamos una
		if profile.current_city is None:
			profile.current_city = now_city

		profile.last_login = now_city
		profile.last_login_lat = PUT['lat']
		profile.last_login_lon = PUT['lon']
		profile.save()
		return self.create_response(request, {"status":True}, response_class = HttpResponse)


class UserProfileResource(ModelResource):

	class Meta:
		object_class = UserProfile
		queryset = UserProfile.objects.all()
		allowed_methods = ['get', 'put']
		include_resource_uri = False
		resource_name = 'profiles'
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = AnonymousApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

	def prepend_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/(?P<pk>\d[\d/-]*)/preview%s$" % (self._meta.resource_name, trailing_slash()),
				self.wrap_view('preview_profile'), name="api_detail_preview"),
		]

	def preview_profile(self, request, **kwargs):
		return self.dispatch_detail(request, **kwargs)

	def connected(self, prof):
		valid_time = getattr(settings, 'TOKEN_DISCONNECTED', 60)
		if time.time() - prof.last_js > valid_time:
			return 'OFF'
		return 'ON'

	def get_detail(self, request, **kwargs):
		#Check if the user is valid
		is_preview = request.path.split('/')[-1] == 'preview'
		if request.user.is_anonymous():
			return self.create_response(request, {"status":False, "errors":[{"type":"AUTH_REQUIRED"}]}, response_class=HttpResponse)
		else:
			if is_preview:
				prof = UserProfile.objects.filter(pk= kwargs['pk'])
				if len(prof) > 0:
					prof = prof[0]
					if prof.active is False:
						return self.create_response(request, {"status":False, "errors":[{"type":"UNKNOWN_USER"}]}, response_class=HttpResponse)
					prof_obj = PreviewProfileObject()
					interests = prof.interested_in.filter()
					for i in interests:
						prof_obj.interested_in.append({"gender":i.gender})

					hometown = prof.hometown
					if hometown is not None:
						prof_obj.hometown['lat'] = hometown.lat
						prof_obj.hometown['lon'] = hometown.lon
						prof_obj.hometown['name'] = hometown.name
						prof_obj.hometown['region'] = hometown.region.name
						prof_obj.hometown['country'] = hometown.region.country.name

					prof_obj.reply_time = prof.reply_time
					prof_obj.main_mission = prof.main_mission
					prof_obj.civil_state = prof.civil_state
					prof_obj.personal_philosophy = prof.personal_philosophy

					conn = self.connected(prof.user)
					if conn == "OFF":
						last = prof.user
						if prof.last_login is not None:
							prof_obj.last_login = prof.last_login.jsonify()
						prof_obj.last_login_date = str(last.last_login)
					elif conn == "AFK":
						prof_obj.last_login_date = "AFK"
					else:
						prof_obj.last_login_date = "ON"
					education= UserProfileStudiedUniversity.objects.filter(user_profile= prof)
					for i in education:
						prof_obj.education.append(i.university.name)

					prof_obj.id = prof.pk
					prof_obj.occupation = prof.occupation

					current = prof.current_city
					if current is not None:
						prof_obj.current['lat'] = current.lat
						prof_obj.current['lon'] = current.lon
						prof_obj.current['name'] = current.name
						prof_obj.current['region'] = current.region.name
						prof_obj.current['country'] = current.region.country.name

					prof_obj.incredible = prof.incredible

					other_locations = prof.other_locations.filter()
					for i in other_locations:
						aux = {}
						aux['lat'] = i.lat
						aux['lon'] = i.lon
						aux['name'] = i.name
						aux['region'] = i.region.name
						aux['country'] = i.region.country.name
						prof_obj.other_locations.append(aux)

					prof_obj.sports = prof.sports

					langs = UserLanguage.objects.filter(user_profile=prof)

					for i in langs:
						aux = {}
						aux['name'] = i.language.name
						aux['level'] = i.level
						prof_obj.languages.append(aux)

					prof_obj.quotes = prof.quotes

					prof_obj.online = self.connected(prof.user)
					prof_obj.sharing = prof.sharing
					prof_obj.pw_opinion = prof.pw_opinion
					prof_obj.political_opinion = prof.political_opinion
					prof_obj.company = prof.company
					prof_obj.reply_rate = prof.reply_rate

					prof_obj.inspired_by = prof.inspired_by
					prof_obj.other_pages = prof.other_pages
					prof_obj.first_name = prof.user.first_name
					prof_obj.enjoy_people = prof.enjoy_people
					prof_obj.gender = prof.gender
					prof_obj.age = prof.get_age()
					prof_obj.all_about_you = prof.all_about_you
					prof_obj.movies = prof.movies
					prof_obj.avatar = prof.avatar

					prof_obj.last_name = prof.user.last_name
					prof_obj.religion = prof.religion

					prof_obj.birthday = str(prof.birthday)
					"""
					if prof.show_birthday == 'F':
						prof_obj.birthday = str(prof.birthday)
					elif prof.show_birthday == 'P':
						prof_obj.birthday = '%s-%s' % (prof.birthday.month, prof.birthday.day)
					else:
						prof_obj.birthday = ""
					"""
					albums = PhotoAlbums.objects.filter(author=prof).order_by('ordering')
					for album in albums:
						album_obj = {}
						album_obj['id'] = album.pk
						album_obj['name'] = album.name
						album_obj['photos'] = []
						photos = Photos.objects.filter(album=album).order_by('ordering')
						for photo in photos:
							photo_obj = {}
							photo_obj['id'] = photo.pk
							photo_obj['big_url'] = photo.big_url
							photo_obj['thumb_url'] = photo.thumb_url
							album_obj['photos'].append(photo_obj)
						prof_obj.albums.append(album_obj)

					for reference in References.objects.filter(receiver = prof).order_by('-created'):
						ref_obj = {}
						sender = reference.sender
						ref_obj['sender_id'] = sender.pk
						ref_obj['first_name'] = sender.user.first_name
						ref_obj['last_name'] = sender.user.last_name
						ref_obj['age'] = sender.get_age()
						ref_obj['online'] = self.connected(sender.user)
						ref_obj['avatar'] = sender.thumb_avatar
						meet = True
						if References.objects.filter(sender = prof, receiver = sender).count():
							meet = False
						ref_obj['meetInPerson'] = meet
						epoch = int(time.mktime(reference.created.timetuple()))
						ref_obj['date'] = epoch
						ref_obj['rating'] = reference.rating
						ref_obj['text'] = reference.text
						if sender.current_city is not None:
							ref_obj['city'] = sender.current_city.stringify()
						else:
							ref_obj['city'] = 'Unknown location'
						#si ya le he mandando una ref
						if References.objects.filter(receiver = sender, sender = prof).count():
							ref_obj['referenced'] = True
						else:
							ref_obj['referenced'] = False
						prof_obj.references.append(ref_obj)

					return self.create_response(request, {"status":True, "data": prof_obj.jsonable()}, response_class=HttpResponse)
				else:
					return self.create_response(request, {"status":True, "data":{}}, response_class=HttpResponse)
			else:
				if request.user.pk != int(kwargs['pk']):
					return self.create_response(request, {"status":False, "errors":[{"type":"FORBIDDEN"}]}, response_class=HttpResponse)
				else:
					prof = UserProfile.objects.filter(user=request.user)
					if len(prof) > 0:
						prof = prof[0]
						if prof.active is False:
							return self.create_response(request, {"status":False, "errors":[{"type":"UNKNOWN_USER"}]}, response_class=HttpResponse)
						prof_obj = EditProfileObject()

						interests = prof.interested_in.filter()
						for i in interests:
							prof_obj.interested_in.append({"gender":i.gender})

						hometown = prof.hometown
						if hometown is not None:
							#import pdb; pdb.set_trace()
							prof_obj.hometown['lat'] = hometown.lat
							prof_obj.hometown['lon'] = hometown.lon
							prof_obj.hometown['name'] = hometown.name
							prof_obj.hometown['region'] = hometown.region.name
							prof_obj.hometown['country'] = hometown.region.country.name

						prof_obj.reply_time = prof.reply_time
						prof_obj.main_mission = prof.main_mission
						prof_obj.birth_month = prof.birthday.month
						prof_obj.civil_state = prof.civil_state
						prof_obj.personal_philosophy = prof.personal_philosophy
						prof_obj.last_login_date = "ON"

						education= UserProfileStudiedUniversity.objects.filter(user_profile= prof)
						for i in education:
							prof_obj.education.append(i.university.name)

						prof_obj.id = prof.pk
						prof_obj.occupation = prof.occupation

						current = prof.current_city
						if current is not None:
							prof_obj.current['lat'] = current.lat
							prof_obj.current['lon'] = current.lon
							prof_obj.current['name'] = current.name
							prof_obj.current['region'] = current.region.name
							prof_obj.current['country'] = current.region.country.name

						prof_obj.pw_state = prof.pw_state
						prof_obj.incredible = prof.incredible

						other_locations = prof.other_locations.filter()
						for i in other_locations:
							aux = {}
							aux['lat'] = i.lat
							aux['lon'] = i.lon
							aux['name'] = i.name
							aux['region'] = i.region.name
							aux['country'] = i.region.country.name
							prof_obj.other_locations.append(aux)

						prof_obj.sports = prof.sports
						langs = UserLanguage.objects.filter(user_profile=prof)
						for i in langs:
							aux = {}
							aux['name'] = i.language.name
							aux['level'] = i.level
							prof_obj.languages.append(aux)

						prof_obj.birth_year = prof.birthday.year
						prof_obj.quotes = prof.quotes

						sn = UserSocialNetwork.objects.filter(user_profile=prof)
						for i in sn:
							aux = {}
							aux['snUsername'] = i.social_network_username
							aux['socialNetwork'] = i.social_network.name
							prof_obj.social_networks.append(aux)

						prof_obj.online = "ON"
						prof_obj.sharing = prof.sharing
						prof_obj.pw_opinion = prof.pw_opinion
						prof_obj.political_opinion = prof.political_opinion
						prof_obj.company = prof.company
						prof_obj.reply_rate = prof.reply_rate

						im = UserInstantMessage.objects.filter(user_profile=prof)
						for i in im:
							aux = {}
							aux['imUsername'] = i.instant_message_username
							aux['instantMessage'] = i.instant_message.name
							prof_obj.instant_messages.append(aux)

						prof_obj.phone = prof.phone
						prof_obj.emails = prof.emails
						prof_obj.inspired_by = prof.inspired_by
						prof_obj.other_pages = prof.other_pages
						prof_obj.first_name = prof.user.first_name
						prof_obj.enjoy_people = prof.enjoy_people
						prof_obj.gender = prof.gender
						prof_obj.age = prof.get_age()
						prof_obj.all_about_you = prof.all_about_you
						prof_obj.movies = prof.movies
						prof_obj.birth_day = prof.birthday.day
						prof_obj.avatar = prof.avatar

						last_login = prof.last_login
						if last_login is not None:
							prof_obj.last_login = last_login.jsonify()

						prof_obj.last_name = prof.user.last_name
						prof_obj.religion = prof.religion
						prof_obj.show_birthday = 'F'

						albums = PhotoAlbums.objects.filter(author=prof).order_by('ordering')
						for album in albums:
							album_obj = {}
							album_obj['id'] = album.pk
							album_obj['name'] = album.name
							album_obj['photos'] = []
							photos = Photos.objects.filter(album=album).order_by('ordering')
							for photo in photos:
								photo_obj = {}
								photo_obj['id'] = photo.pk
								photo_obj['big_url'] = photo.big_url
								photo_obj['thumb_url'] = photo.thumb_url
								album_obj['photos'].append(photo_obj)
							prof_obj.albums.append(album_obj)

						for reference in References.objects.filter(receiver = prof).order_by('-created'):
							ref_obj = {}
							sender = reference.sender
							ref_obj['sender_id'] = sender.pk
							ref_obj['first_name'] = sender.user.first_name
							ref_obj['last_name'] = sender.user.last_name
							ref_obj['age'] = sender.get_age()
							ref_obj['online'] = self.connected(sender.user)
							ref_obj['avatar'] = sender.thumb_avatar
							meet = True
							if References.objects.filter(sender = prof, receiver = sender).count():
								meet = False
							ref_obj['meetInPerson'] = meet
							epoch = int(time.mktime(reference.created.timetuple()))
							ref_obj['date'] = epoch
							ref_obj['rating'] = reference.rating
							ref_obj['text'] = reference.text
							if sender.current_city is not None:
								ref_obj['city'] = sender.current_city.stringify()
							else:
								ref_obj['city'] = 'Unknown location'
							if References.objects.filter(receiver = sender, sender = prof).count():
								ref_obj['referenced'] = True
							else:
								ref_obj['referenced'] = False
							prof_obj.references.append(ref_obj)

						return self.create_response(request, {"status":True, "data": prof_obj.jsonable()}, response_class=HttpResponse)
					else:
						return self.create_response(request, {"status":True, "data":{}}, response_class=HttpResponse)

	def is_valid_put(self, request):
		POST = json.loads(request.raw_post_data)
		errors = []
		field_req = {"type":"FIELD_REQUIRED", "extras":[]}
		not_empty = {"type":"NOT_EMPTY", "extras":[]}
		too_long = {"type":"TOO_LONG", "extras":[]}
		invalid = {"type":"INVALID", "extras":[]}

		"""
		if POST.has_key('XXX'):
			if POST['XXX'] == "":
				not_empty['extras'].append('XXX')
			elif POST['XXX'] not in []:
				invalid['extras'].append('XXX')
		else:
			field_req['extras'].append('XXX')
		"""
		if POST.has_key('gender'):
			if POST['gender'] == "":
				not_empty['extras'].append('gender')
			elif POST['gender'] not in ['Male', 'Female']:
				invalid['extras'].append('gender')
		else:
			field_req['extras'].append('gender')

		if POST['socialNetworks']:
			if not isinstance(POST['socialNetworks'], list):
				invalid['extras'].append('socialNetworks')
			else:
				for i in POST['socialNetworks']:
					if not isinstance(i, dict):
						if 'socialNetworks' not in invalid['extras']:
							invalid['extras'].append('socialNetworks')
					else:
						if not i.has_key('snUsername') or not isinstance(i['snUsername'], unicode):
							if 'socialNetworks' not in invalid['extras']:
								invalid['extras'].append('socialNetworks')
						else:
							if len(i['snUsername']) > 40:
								too_long['extras'].append('socialNetworks')
						if not i.has_key('socialNetwork'):
							if 'socialNetworks' not in invalid['extras']:
								invalid['extras'].append('socialNetworks')
						else:
							if len(SocialNetwork.objects.filter(name=i['socialNetwork'])) == 0:
								if 'socialNetworks' not in invalid['extras']:
									invalid['extras'].append('socialNetworks')

		if POST['instantMessages']:
			if not isinstance(POST['instantMessages'], list):
				invalid['extras'].append('instantMessages')
			else:
				for i in POST['instantMessages']:
					if not isinstance(i, dict):
						if 'instantMessages' not in invalid['extras']:
							invalid['extras'].append('instantMessages')
					else:
						if not i.has_key('imUsername') or not isinstance(i['imUsername'], unicode):
							if 'instantMessages' not in invalid['extras']:
								invalid['extras'].append('instantMessages')
						else:
							if len(i['imUsername']) > 40:
								too_long['extras'].append('instantMessages')
						if not i.has_key('instantMessage'):
							if 'instantMessages' not in invalid['extras']:
								invalid['extras'].append('instantMessages')
						else:
							if len(InstantMessage.objects.filter(name=i['instantMessage'])) == 0:
								if 'instantMessages' not in invalid['extras']:
									invalid['extras'].append('instantMessages')


		if POST.has_key('interestedIn'):
			if not isinstance(POST['interestedIn'], list):
				invalid['extras'].append('interestedIn')
			elif len(POST['interestedIn']) != 0:
				if len(POST['interestedIn']) != 1:
					invalid['extras'].append('interestedIn')
				elif not isinstance(POST['interestedIn'][0], dict):
					invalid['extras'].append('interestedIn')
				elif not POST['interestedIn'][0].has_key('gender'):
					invalid['extras'].append('interestedIn')
				elif POST['interestedIn'][0]['gender'] not in ['Male', 'Female', 'Both']:
					invalid['extras'].append('interestedIn')

		if POST.has_key('civilState'):
			if POST['civilState'] not in ['', 'SI', 'EN', 'MA', 'WI', 'IR', 'IO', 'IC', 'DI', 'SE']:
				invalid['extras'].append('civilState')

		if POST.has_key('languages'):
			if not isinstance(POST['languages'], list):
				invalid['extras'].append('languages')
			else:
				for i in POST['languages']:
					if not isinstance(i, dict):
						if not 'languages' in invalid['extras']:
							invalid['extras'].append('languages')
					else:
						if not i.has_key("name"):
							if not 'languages' in invalid['extras']:
								invalid['extras'].append('languages')
							elif i["name"] not in [lang.name for lang in Language.objects.all()]:
								if not 'languages' in invalid['extras']:
									invalid['extras'].append('languages')
						if not i.has_key("level"):
							if not 'languages' in invalid['extras']:
								invalid['extras'].append('languages')
						elif i['level'] not in ["intermediate", "expert", "beginner"]:
							if not 'languages' in invalid['extras']:
								invalid['extras'].append('languages')

		if POST.has_key('hometown'):
			if not isinstance(POST['hometown'], dict):
				invalid['extras'].append('hometown')
			else:
				if len(POST['hometown'].keys()) != 0:
					if not (POST['hometown'].has_key('lat') and POST['hometown'].has_key('lon') and POST['hometown'].has_key('country') and POST['hometown'].has_key('name')):
						invalid['extras'].append('hometown')

		if POST.has_key('current'):
			if not isinstance(POST['current'], dict):
				invalid['extras'].append('current')
			else:
				if len(POST['current'].keys()) != 0:
					if not (POST['current'].has_key('lat') and POST['current'].has_key('lon') and POST['current'].has_key('country') and POST['current'].has_key('name')):
						invalid['extras'].append('current')

		if POST.has_key('otherLocations'):
			if not isinstance(POST.has_key('otherLocations'), list):
				for i in POST['otherLocations']:
					if isinstance(i, dict) and len(i.keys()) != 0:
						if not (i.has_key('lat') and i.has_key('lon') and i.has_key('country') and i.has_key('name')):
							invalid['extras'].append('otherLocations')

		if POST.has_key('education'):
			if not isinstance(POST['education'], list):
				invalid['extras'].append('education')
			else:
				for i in POST['education']:
					if not isinstance(i, unicode):
						if 'education' not in invalid['extras']:
							invalid['extras'].append('education')
					elif len(i) > 100:
							too_long['extras'].append('education')

		if POST.has_key('politicalOpinion'):
			if len(POST['politicalOpinion']) > 500:
				too_long['extras'].append('politicalOpinion')
		else:
			field_req['extras'].append('politicalOpinion')

		if POST.has_key('mainMission'):
			if len(POST['mainMission']) > 100:
				too_long['extras'].append('mainMission')
		else:
			field_req['extras'].append('mainMission')

		if POST.has_key('company'):
			if len(POST['company']) > 100:
				too_long['extras'].append('company')
		else:
			field_req['extras'].append('company')

		if POST.has_key('personalPhilosophy'):
			if len(POST['personalPhilosophy']) > 1000:
				too_long['extras'].append('personalPhilosophy')
		else:
			field_req['extras'].append('personalPhilosophy')

		if POST.has_key('sports'):
			if len(POST['sports']) > 500:
				too_long['extras'].append('sports')
		else:
			field_req['extras'].append('sports')

		if POST.has_key('sharing'):
			if len(POST['sharing']) > 1000:
				too_long['extras'].append('sharing')
		else:
			field_req['extras'].append('sharing')

		if POST.has_key('incredible'):
			if len(POST['incredible']) > 1000:
				too_long['extras'].append('incredible')
		else:
			field_req['extras'].append('incredible')

		if POST.has_key('quotes'):
			if len(POST['quotes']) > 500:
				too_long['extras'].append('quotes')
		else:
			field_req['extras'].append('quotes')

		if POST.has_key('pwOpinion'):
			if len(POST['pwOpinion']) > 500:
				too_long['extras'].append('pwOpinion')
		else:
			field_req['extras'].append('pwOpinion')

		if POST.has_key('otherPages'):
			if len(POST['otherPages']) > 500:
				too_long['extras'].append('otherPages')
		else:
			field_req['extras'].append('otherPages')

		if POST.has_key('emails'):
			if len(POST['emails']) > 100:
				too_long['extras'].append('emails')
		else:
			field_req['extras'].append('emails')

		if POST.has_key('phone'):
			if len(POST['phone']) > 100:
				too_long['extras'].append('phone')
		else:
			field_req['extras'].append('phone')

		if POST.has_key('inspiredBy'):
			if len(POST['inspiredBy']) > 500:
				too_long['extras'].append('inspiredBy')
		else:
			field_req['extras'].append('inspiredBy')

		if POST.has_key('enjoyPeople'):
			if len(POST['enjoyPeople']) > 500:
				too_long['extras'].append('enjoyPeople')
		else:
			field_req['extras'].append('enjoyPeople')

		if POST.has_key('gender'):
			if POST['gender'] not in ['Male', 'Female']:
				invalid['extras'].append('gender')
		else:
			field_req['extras'].append('gender')

		if POST.has_key('allAboutYou'):
			if len(POST['allAboutYou']) > 500:
				too_long['extras'].append('allAboutYou')
		else:
			field_req['extras'].append('allAboutYou')

		if POST.has_key('movies'):
			if len(POST['movies']) > 500:
				too_long['extras'].append('movies')
		else:
			field_req['extras'].append('movies')

		if POST.has_key('birthDay'):
			if POST['birthDay'] == "":
				not_empty['extras'].append('birthDay')
			try:
				if int(POST['birthDay']) < 1 or int(POST['birthDay']) > 31:
					invalid['extras'].append('birthDay')
			except:
				invalid['extras'].append('birthDay')
		else:
			field_req['extras'].append('birthDay')

		if POST.has_key('birthMonth'):
			if POST['birthMonth'] == "":
				not_empty['extras'].append('birthMonth')
			try:
				if int(POST['birthMonth']) < 1 or int(POST['birthMonth']) > 12:
					invalid['extras'].append('birthMonth')
			except:
				invalid['extras'].append('birthMonth')
		else:
			field_req['extras'].append('birthMonth')

		if POST.has_key('birthYear'):
			if POST['birthYear'] == "":
				not_empty['extras'].append('birthYear')
			try:
				if int(POST['birthYear']) < 1900 or int(POST['birthYear']) > datetime.now().year - 18:
					invalid['extras'].append('birthYear')
			except:
				invalid['extras'].append('birthYear')
		else:
			field_req['extras'].append('birthYear')


		try:
			parser.parse('%s-%s-%s' % (POST['birthYear'], POST['birthMonth'], POST['birthDay']))
		except:
			invalid['extras'].append('birthday')

		if POST.has_key('religion'):
			if len(POST['religion']) > 500:
				too_long['extras'].append('religion')
		else:
			field_req['extras'].append('religion')

		if POST.has_key('occupation'):
			if len(POST['occupation']) > 100:
				too_long['extras'].append('occupation')
		else:
			field_req['extras'].append('occupation')
		"""
		if POST.has_key('albums'):
			if isinstance(POST['albums'], list):
				for item in POST['albums']:
					if (isinstance(item, dict)):
						if not item.has_key('name'):
							invalid['extras'].append('albums')
							break
						if not item.has_key('photos'):
							invalid['extras'].append('albums')
							break
						elif isinstance(item['photos'], list):
							for item2 in item['photos']:
								if isinstance(item2, dict):
										if item2.has_key('id') and item2.has_key('thumbUrl') and item2.has_key('bigUrl'):
											pass
										else:
											invalid['extras'].append('photos')
											break
								else:
									invalid['extras'].append('photos')
									break
						else:
							invalid['extras'].append('photos')
							break
					else:
						invalid['extras'].append('albums')
						break
			else:
				invalid['extras'].append('albums')
		else:
		  field_req['extras'].append('albums')
		"""
		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(too_long['extras']) > 0:
			errors.append(too_long)
		if len(invalid['extras']) > 0:
			errors.append(invalid)
		return errors

	def put_detail(self, request, **kwargs):
		#import pdb; pdb.set_trace()
		POST = json.loads(request.raw_post_data)
		#We need to check if the user thar requested the put is the same user that owns the profile
		try:
			if not int(kwargs['pk']) == UserProfile.objects.get(user = request.user).pk:
				return self.create_response(request, {"status":False, "errors":[{"type":"FORBIDDEN"}]}, response_class=HttpResponse)
		except:
			return self.create_response(request, {"status":False, "errors":[{"type":"INTERNAL_ERROR"}]}, response_class=HttpResponse)

		#We need to check that received data is valid
		try:
			errors = self.is_valid_put(request)
			if len(errors) > 0:
				return self.create_response(request, {"status":False, "errors":errors}, response_class=HttpResponse)
		except:
			return self.create_response(request, {"status":False, "errors":[{"type":"INTERNAL_ERROR"}]}, response_class=HttpResponse)

		#We need to update the needed fields
		prof = UserProfile.objects.get(pk=kwargs['pk'])
		if prof.active is False:
			return self.create_response(request, {"status":False, "errors":[{"type":"UNKNOWN_USER"}]}, response_class=HttpResponse)

		"""
		TODO
		avatar = models.CharField(max_length=max_long_len, default= django_settings.ANONYMOUS_BIG)
		medium_avatar = models.CharField(max_length=max_long_len, default= django_settings.ANONYMOUS_AVATAR, blank = True)
		thumb_avatar = models.CharField(max_length=max_long_len, default= django_settings.ANONYMOUS_THUMB, blank = True)
		"""

		prof.birthday =parser.parse('%s-%s-%s' % (POST['birthYear'], POST['birthMonth'], POST['birthDay']))
		#prof.show_birthday = POST['showBirthday']
		prof.gender = POST['gender']
		prof.interested_in.clear()

		if (len(POST['interestedIn']) != 0):
			prof.interested_in.add(Interests.objects.get(gender__contains=POST['interestedIn'][0]['gender']))

		prof.civil_state = POST['civilState']

		[i.delete() for i in UserLanguage.objects.filter(user_profile=prof)]
		for i in POST['languages']:
			if len(Language.objects.filter(name=i['name'])) > 0:
				lang = Language.objects.get(name=i['name'])
			else:
				lang = Language.objects.create(name=i['name'])
			UserLanguage.objects.create(user_profile=prof, language=lang, level=i['level'])
		# Locations
		if  POST['current']:
			if not POST['current'].has_key('region'):
				POST['current']['region'] = 'No region'
			prof.current_city = City.objects.saveLocation(country=POST['current']['country'], region=POST['current']['region'], name=POST['current']['name'], lat=POST['current']['lat'], lon=POST['current']['lon'])
		else:
			prof.current_city = None

		if POST['hometown']:
			if not POST['hometown'].has_key('region'):
				POST['hometown']['region'] = 'No region'
			prof.hometown = City.objects.saveLocation(country=POST['hometown']['country'], region=POST['hometown']['region'], name=POST['hometown']['name'], lat=POST['hometown']['lat'], lon=POST['hometown']['lon'])
		else:
			prof.hometown = None

		prof.other_locations.clear()
		if POST['otherLocations']:
			for i in POST['otherLocations']:
				if not i.has_key('region'):
					i['region'] = 'No region'
				prof.other_locations.add(City.objects.saveLocation(country=i['country'], region=i['region'], name=i['name'], lat=i['lat'], lon=i['lon']))

		prof.emails = POST['emails']
		prof.phone = POST['phone']

		[i.delete() for i in UserSocialNetwork.objects.filter(user_profile=prof)]
		for i in POST['socialNetworks']:
			UserSocialNetwork.objects.create(user_profile=prof, social_network=SocialNetwork.objects.get(name=i['socialNetwork']), social_network_username=i['snUsername'])

		[i.delete() for i in UserInstantMessage.objects.filter(user_profile=prof)]
		for i in POST['instantMessages']:
			UserInstantMessage.objects.create(user_profile=prof, instant_message=InstantMessage.objects.get(name=i['instantMessage']), instant_message_username=i['imUsername'])

		prof.all_about_you = POST['allAboutYou']
		prof.main_mission = POST['mainMission']
		prof.occupation = POST['occupation']
		prof.company = POST['company']

		[i.delete() for i in UserProfileStudiedUniversity.objects.filter(user_profile=prof)]
		for i in POST['education']:
			if len(University.objects.filter(name=i)) > 0:
				univ = University.objects.get(name=i)
			else:
				univ = University.objects.create(name=i)
			UserProfileStudiedUniversity.objects.create(user_profile=prof, university=univ, )

		prof.personal_philosophy = POST['personalPhilosophy']
		prof.political_opinion = POST['politicalOpinion']
		prof.religion = POST['religion']
		prof.enjoy_people = POST['enjoyPeople']
		prof.movies = POST['movies']
		prof.sports = POST['sports']
		prof.other_pages = POST['otherPages']
		prof.sharing = POST['sharing']
		prof.incredible = POST['incredible']
		prof.inspired_by = POST['inspiredBy']
		prof.quotes = POST['quotes']
		prof.pw_opinion = POST['pwOpinion']

		#Photo albums
		"""
		prof_albums = PhotoAlbums.objects.filter(author=prof).delete()
		album_ordering = 1
		for album in POST['albums']:
			album_obj = PhotoAlbums.objects.create(album_id=album['id'], name=album['name'], ordering=album_ordering, author=prof)
			photo_ordering = 1
			for photo in album['photos']:
				Photos.objects.create(thumb_url=photo['thumb_url'],big_url=photo['big_url'], photo_id=photo['id'],author=prof, album=album_obj, ordering=photo_ordering)
				photo_ordering = photo_ordering + 1
				album_ordering = album_ordering + 1
		"""

		prof.save()
		return self.create_response(request, {"status":True}, response_class=HttpResponse)

	def put_list(self, request, **kwargs):
		return self.create_response(request, {"status":False, "errors":[{"type":"METHOD_NOT_ALLOWED"}]}, response_class=HttpResponse)

	def parse_date(self, initial_date):
		try:
			year = initial_date[:4]
			month = initial_date[5:7]
			day = initial_date[8:10]
			result = int(time.mktime(time.strptime('%s-%s-%s 23:59:59' % (year, month, day), '%Y-%m-%d %H:%M:%S'))) - time.timezone
		except:
			result = None
		return result

	def validate_people_search(self, GET):
		errors = []
		field_req = {"type": 'FIELD_REQUIRED', "extras":[]}
		not_empty = {"type": 'NOT_EMPTY', "extras":[]}
		invalid_field = {"type": 'INVALID_FIELD', "extras":[]}

		#Mandatory params
		if GET.has_key('startAge'):
			if GET['startAge'] == "":
				not_empty['extras'].append('startAge')
		else:
			field_req['extras'].append('startAge')

		if GET.has_key('endAge'):
			if GET['endAge'] == "":
				not_empty['extras'].append('endAge')
		else:
			field_req['extras'].append('endAge')

		if GET.has_key('language'):
			if GET['language'] == "":
				not_empty['extras'].append('language')
		else:
			field_req['extras'].append('language')

		if GET.has_key('page'):
			if GET['page'] == "":
				not_empty['extras'].append('page')
		else:
			field_req['extras'].append('page')

		if GET.has_key('gender'):
			if GET['gender'] == "":
				not_empty['extras'].append('gender')
		else:
			field_req['extras'].append('gender')

		#Optional params
		if GET.has_key('location'):
			if GET['location'] == "":
				not_empty['extras'].append('location')

		#Other checks
		#startAge >=18
		if GET.has_key('startAge') and GET['startAge'] < 1:
			invalid_field['extras'].append('startAge')
		#endAge >= 18
		if GET.has_key('endAge') and GET['endAge'] < 1:
			invalid_field['extras'].append('endAge')
		#startAge >= endAge
		if GET.has_key('startAge') and GET.has_key('endAge') and GET['endAge'] < GET['startAge']:
			invalid_field['extras'].append('age')
		#gender in male, female both
		if GET.has_key('gender') and GET['gender'] not in ['Male', 'Female', 'Both']:
			invalid_field['extras'].append('gender')
		#people search
		if GET.has_key('hero') and len(GET['hero']) == 0:
			not_empty['extras'].append('hero')

		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(invalid_field['extras']) > 0:
			errors.append(invalid_field)
		return errors
	def validate_accomodation_search(self, GET):
		errors = []
		field_req = {"type": 'FIELD_REQUIRED', "extras":[]}
		not_empty = {"type": 'NOT_EMPTY', "extras":[]}
		invalid_field = {"type": 'INVALID_FIELD', "extras":[]}

		#Mandatory params
		if GET.has_key('capacity'):
			if GET['capacity'] == "":
				not_empty['extras'].append('capacity')
		else:
			field_req['extras'].append('capacity')

		if GET.has_key('startAge'):
			if GET['startAge'] == "":
				not_empty['extras'].append('startAge')
		else:
			field_req['extras'].append('startAge')

		if GET.has_key('endAge'):
			if GET['endAge'] == "":
				not_empty['extras'].append('endAge')
		else:
			field_req['extras'].append('endAge')

		if GET.has_key('language'):
			if GET['language'] == "":
				not_empty['extras'].append('language')
		else:
			field_req['extras'].append('language')

		if GET.has_key('type'):
			if GET['type'] == "":
				not_empty['extras'].append('type')
			if GET['type'] not in ['Host', 'Applicant']:
				invalid_field['extras'].append('type')
		else:
			field_req['extras'].append('type')

		if GET.has_key('page'):
			if GET['page'] == "":
				not_empty['extras'].append('page')
		else:
			field_req['extras'].append('page')

		if GET.has_key('gender'):
			if GET['gender'] == "":
				not_empty['extras'].append('gender')
		else:
			field_req['extras'].append('gender')

		#Optional params
		if GET.has_key('startDate'):
			if GET['startDate'] == "":
				not_empty['extras'].append('startDate')

		if GET.has_key('endDate'):
			if GET['endDate'] == "":
				not_empty['extras'].append('endDate')

		if GET.has_key('wings'):
			if GET['wings'] == "":
				not_empty['extras'].append('wings')

		#Other checks
		#capacity >= 1
		if GET.has_key('capacity') and GET['capacity'] < 1:
			invalid_field['extras'].append('capacity')
		#startAge >=18
		if GET.has_key('startAge') and GET['startAge'] < 1:
			invalid_field['extras'].append('startAge')
		#endAge >= 18
		if GET.has_key('endAge') and GET['endAge'] < 1:
			invalid_field['extras'].append('endAge')
		#startAge >= endAge
		if GET.has_key('startAge') and GET.has_key('endAge') and GET['endAge'] < GET['startAge']:
			invalid_field['extras'].append('age')
		#startDate >=today
		if GET.has_key('startDate') and self.parse_date(GET['startDate']) is not None and self.parse_date(GET['startDate']) < time.time():
			invalid_field['extras'].append('startDate')
		#endDate >= today
		if GET.has_key('endDate') and self.parse_date(GET['endDate']) is not None and self.parse_date(GET['endDate']) < time.time():
			invalid_field['extras'].append('endDate')
		#startDate >= endDate
		if GET.has_key('startDate') and GET.has_key('endDate') and self.parse_date(GET['endDate']) is not None and self.parse_date(GET['startDate']) is not None:
			endDate = self.parse_date(GET['endDate'])
			startDate = self.parse_date(GET['startDate'])
			if endDate < startDate:
				invalid_field['extras'].append('date')

		#gender in male, female both
		if GET.has_key('gender') and GET['gender'] not in ['Male', 'Female', 'Both']:
			invalid_field['extras'].append('gender')


		if len(field_req['extras']) > 0:
			errors.append(field_req)
		if len(not_empty['extras']) > 0:
			errors.append(not_empty)
		if len(invalid_field['extras']) > 0:
			errors.append(invalid_field)

		return errors

	def make_people_search_filters(self, GET):
		#We have to filter by: birthday (UP)*-OK, language (up)*-OK, gender( up)*-OK, capacity (w)*-OK, wings (w)-OK, start_date & end_date (w)-OK, type*
		min_year = datetime.today().year
		min_month = datetime.today().month
		min_day = datetime.today().day
		min_year = min_year - int(GET['startAge'])
		max_year = datetime.today().year
		max_month = datetime.today().month
		max_day = datetime.today().day
		max_year = max_year - int(GET['endAge'])
		min_birthday = '%s-%s-%s' % (min_year, min_month, min_day)
		max_birthday = '%s-%s-%s' % (max_year, max_month, max_day)

		result = Q(birthday__gte=max_birthday)&Q(birthday__lte=min_birthday)&Q(active=True)&Q(user__is_active=True)
		if GET['language'] != 'all':
			result = result &Q(languages__name= GET['language'])
		if GET['gender'] != 'Both':
			result = result & Q(gender=GET['gender'])
		if 'location' in GET:
			result = result & (Q(current_city__name=GET['location'])|Q(current_city__region__name__icontains=GET['location'])|Q(current_city__region__country__name__icontains=GET['location'])|Q(last_login__name=GET['location'])|Q(last_login__region__name__icontains=GET['location'])|Q(last_login__region__country__name__icontains=GET['location']))
		if 'hero' in GET:
			result = result & (Q(full_name__icontains=GET['hero']))
		return result

	def make_accomodation_search_filters(self, GET):
		#We have to filter by: birthday (UP)*-OK, language (up)*-OK, gender( up)*-OK, capacity (w)*-OK, wings (w)-OK, start_date & end_date (w)-OK, type*
		min_year = datetime.today().year
		min_month = datetime.today().month
		min_day = datetime.today().day
		min_year = min_year - int(GET['startAge'])
		max_year = datetime.today().year
		max_month = datetime.today().month
		max_day = datetime.today().day
		max_year = max_year - int(GET['endAge'])
		min_birthday = '%s-%s-%s' % (min_year, min_month, min_day)
		max_birthday = '%s-%s-%s' % (max_year, max_month, max_day)
		if GET['type'] == 'Host':
			result = Q(birthday__gte=max_birthday)&Q(birthday__lte=min_birthday)&Q(wing__accomodation__capacity__gte= GET['capacity'])&Q(active=True)&Q(wing__status__in=['Y', 'M'])
			if GET['language'] != 'all':
				result = result &Q(languages__name= GET['language'])
			if GET['gender'] != 'Both':
				result = result & Q(gender=GET['gender'])
			if 'wings' in GET:
				result = result & (Q(wing__city__name__icontains=GET['wings'])|Q(wing__city__region__name__icontains=GET['wings'])|Q(wing__city__region__country__name__icontains=GET['wings']))
			if 'startDate' in GET:
				date_start = datetime.strptime('%s 00:00:00' % GET['startDate'], '%Y-%m-%d %H:%M:%S')
				result = result & (Q(wing__date_start__lte=date_start)|Q(wing__date_start__isnull=True))
			if 'endDate' in GET:
				date_end = datetime.strptime('%s 23:59:59' % GET['endDate'], '%Y-%m-%d %H:%M:%S')
				result = result & (Q(wing__date_end__gte=date_end)|Q(wing__date_end__isnull=True))
		else:
			result = Q(birthday__gte=max_birthday)&Q(birthday__lte=min_birthday)&Q(publicrequestwing__capacity__gte= GET['capacity'])&Q(active=True)&Q(wing__status__in=['Y', 'M'])
			if GET['language'] != 'all':
				result = result &Q(languages__name= GET['language'])
			if GET['gender'] != 'Both':
				result = result & Q(gender=GET['gender'])
			if 'wings' in GET:
				result = result & (Q(publicrequestwing__city__name__icontains=GET['wings'])|Q(publicrequestwing__city__region__name__icontains=GET['wings'])|Q(publicrequestwing__city__region__country__name__icontains=GET['wings']))
			if 'startDate' in GET:
				date_start = datetime.strptime('%s 00:00:00' % GET['startDate'], '%Y-%m-%d %H:%M:%S')
				result = result & Q(publicrequestwing__date_end__gte=date_start)
			else:
				date_start_mod = datetime.today()
				date_start_year = date_start_mod.year
				date_start_month = date_start_mod.month
				date_start_day = date_start_mod.day
				date_start = datetime.strptime('%s/%s/%s 00:00:00' % (date_start_year, date_start_month, date_start_day), '%Y/%m/%d %H:%M:%S')
				result = result & Q(publicrequestwing__date_end__gte=date_start)
			if 'endDate' in GET:
				date_end = datetime.strptime('%s 23:59:59' % GET['endDate'], '%Y-%m-%d %H:%M:%S')
				result = result & Q(publicrequestwing__date_start__lte=date_end)
		return result

	def make_accomodation_publicreq_search_filters(self, GET, prof):
		result = Q(capacity__gte= GET['capacity']) & Q(author=prof)
		if 'wings' in GET:
			result = result & Q(city__name__icontains=GET['wings'])
		if 'startDate' in GET:
			date_start = datetime.strptime('%s 00:00:00' % GET['startDate'], '%Y-%m-%d %H:%M:%S')
			result = result & Q(date_end__gte=date_start)
		else:
			date_start_mod = datetime.today()
			date_start_year = date_start_mod.year
			date_start_month = date_start_mod.month
			date_start_day = date_start_mod.day
			date_start = datetime.strptime('%s/%s/%s 00:00:00' % (date_start_year, date_start_month, date_start_day), '%Y/%m/%d %H:%M:%S')
			result = result & Q(date_end__gte=date_start)
		if 'endDate' in GET:
			date_end = datetime.strptime('%s 23:59:59' % GET['endDate'], '%Y-%m-%d %H:%M:%S')
			result = result & Q(date_start__lte=date_end)
		return result


	def parse_languages(self, prof):
		res = []
		langs = UserLanguage.objects.filter(user_profile=prof)
		for i in langs:
			res.append({"name": i.language.name, "level": i.level})
		return res

	def paginate(self, data, GET):
		page_size=20
		num_page = int(GET.get('page', 1))
		count = len(data)
		endResult = min(num_page * page_size, count)
		startResult = min((num_page - 1) * page_size + 1, endResult)
		if startResult < page_size * (num_page -1) + 1:
			#import pdb; pdb.set_trace()
			num_page = round(count/page_size)
			if count%page_size != 0:
				num_page = num_page + 1
			endResult = count
			startResult = ((num_page -1) * page_size) + 1
		elif num_page < 0:
			num_page=1
			startResult = 1
			endResult = min(num_page * page_size, count)
		paginator = Paginator(data, page_size)
		if count == 0:
			data = {}
			data["profiles"] = []
			data["count"] = count
			data["startResult"] = 0
			data["endResult"] = 0
		else:
			try:
				page = paginator.page(num_page)
			except InvalidPage:
				return self.create_response(request, {"status":False, "errors": [{"type":"PAGE_NO_RESULTS"}]}, response_class = HttpResponse)
			data = {}
			data["profiles"] = [i for i in page.object_list]
			data["count"] = count
			data["startResult"] = startResult
			data["endResult"] = endResult

		return data

	def try_to_fit(self, profiles, GET):
		page_size=20
		num_page = int(GET.get('page', 1))
		count = len(profiles)
		endResult = num_page * page_size
		startResult = (num_page - 1) * page_size + 1
		if count < startResult:
			return False
		elif count < endResult:
			return False
		return True

	def get_list(self, request, **kwargs):
		if request.GET.has_key('wingType'):
			if request.GET['wingType'] == 'people':
				return self.search_people(request, **kwargs)
			else:
				return self.create_response(request, {"errors": {"type":"INVALID", "extras":["wingType"]}, "status":False}, response_class=HttpForbidden)
		else:
			return self.search_accomodation(request, **kwargs)

	def get_paginated_profiles(self, profiles, GET):
		#This function receives a list, and has to return a sublist of the original list in a range.
		#If the list consist on profiles from 1-60 and the pagination needs page 2 (profs 21-40, both included)
		page_size=20
		num_page = int(GET.get('page', 1))
		count = len(profiles)
		endResult = min(num_page * page_size, count)
		startResult = min((num_page - 1) * page_size + 1, endResult)
		if startResult < page_size * (num_page -1) + 1:
			#import pdb; pdb.set_trace()
			num_page = round(count/page_size)
			if count%page_size != 0:
				num_page = num_page + 1
			endResult = count
			startResult = ((num_page -1) * page_size) + 1
		elif num_page < 0:
			num_page=1
			startResult = 1
			endResult = min(num_page * page_size, count)
		paginator = Paginator(profiles, page_size)
		if count == 0:
			return [], 0, 0, 0
		else:
			try:
				page = paginator.page(num_page)
			except InvalidPage:
				[]
			return [i for i in page.object_list], count, startResult, endResult

	def fill_domain_search_people(self, all_profiles, GET):
		profiles, count, start, end = self.get_paginated_profiles(all_profiles, GET)
		search_list = SearchObjectManager()

		for prof in profiles:
			search_obj = SearchObject()
			search_obj.profile_id = prof.pk
			search_obj.ctrl_user = prof.user
			search_obj.first_name = prof.user.first_name
			search_obj.last_name = prof.user.last_name
			if prof.current_city:
				search_obj.current = {"name": prof.current_city.name, "region": prof.current_city.region.name, "country": prof.current_city.region.country.name}
			else:
				search_obj.current= {}

			search_obj.avatar = prof.medium_avatar
			search_obj.age = prof.get_age()
			search_obj.online = self.connected(prof) == 'ON'
			search_obj.reply_rate = prof.reply_rate
			search_obj.reply_time = prof.reply_time
			search_obj.languages = self.parse_languages(i)
			search_obj.all_about_you = prof.all_about_you
			search_obj.date_joined = self.parse_date(str(prof.user.date_joined))
			if prof.last_login:
				search_obj.last_login = prof.last_login.jsonify()
			if not search_obj.online:
				search_obj.last_login_date = prof.user.last_login

			for j in Wing.objects.filter(author=i, status__in=['Y', 'M']):
					if j.get_class_name() not in search_obj.wings:
						search_obj.wings.append(j.get_class_name())

			n_photos = 0
			for k in Photos.objects.filter(author=i):
				n_photos = n_photos + 1

			search_obj.n_photos = n_photos
			search_obj.search_score = prof.search_score

			search_list.objects.append(search_obj)

		return search_list, count, start, end


	def search_people(self, request, **kwargs):
		valid_time = getattr(settings, 'TOKEN_DISCONNECTED', 60)
		errors = self.validate_people_search(request.GET)
		if len(errors) > 0:
			return self.create_response(request, {"errors": errors, "status":False}, response_class=HttpForbidden)
		#We have no problem with the given filters
		filters = self.make_people_search_filters(request.GET)

		#Now, we have to search online user with the givern filters and ordering by score
		profiles = UserProfile.objects.filter(filters & Q(last_js__gte=time.time() - valid_time)).distinct().order_by('-search_score')
		#Now let's see if the profiles we got fit the sample, or we have to fill with offline
		if self.try_to_fit(profiles, request.GET):
			search_list, count, start, end = self.fill_domain_search_people(profiles, request.GET)
		else:
			profiles_off = UserProfile.objects.filter(filters & Q(last_js__lt=time.time() - valid_time)).distinct().order_by('-search_score')
			search_list, count, start, end = self.fill_domain_search_people([i for i in profiles] + [i for i in profiles_off], request.GET)

		if not isinstance(request.user, User):
			search_list.make_dirty()

		data = {}
		data['profiles'] = search_list.jsonable()
		data['count'] = count
		data['startResult'] = start
		data['endResult'] = end
		return self.create_response(request, {"data": data, "status":True}, response_class=HttpResponse)

	def fill_domain_search_accomodation(self, all_profiles, GET):
		profiles, count, start, end = self.get_paginated_profiles(all_profiles, GET)
		search_list = SearchObjectManager()

		for prof in profiles:
			search_obj = SearchObject()
			search_obj.profile_id = prof.pk
			search_obj.ctrl_user = prof.user
			search_obj.first_name = prof.user.first_name
			search_obj.last_name = prof.user.last_name
			if prof.current_city:
				search_obj.current = {"name": prof.current_city.name, "region": prof.current_city.region.name, "country": prof.current_city.region.country.name}
			else:
				search_obj.current= {}

			search_obj.avatar = prof.medium_avatar
			search_obj.age = prof.get_age()
			search_obj.online = self.connected(prof) == 'ON'
			search_obj.reply_rate = prof.reply_rate
			search_obj.reply_time = prof.reply_time
			search_obj.languages = self.parse_languages(i)
			search_obj.all_about_you = prof.all_about_you
			search_obj.date_joined = self.parse_date(str(prof.user.date_joined))
			if prof.last_login:
				search_obj.last_login = prof.last_login.jsonify()
			if not search_obj.online:
				search_obj.last_login_date = prof.user.last_login

			for j in Wing.objects.filter(author=i, status__in=['Y', 'M']):
					if j.get_class_name() not in search_obj.wings:
						search_obj.wings.append(j.get_class_name())

			n_photos = 0
			for k in Photos.objects.filter(author=i):
				n_photos = n_photos + 1

			search_obj.n_photos = n_photos
			search_obj.search_score = prof.search_score

			if GET['type'] == 'Applicant':
				filters = self.make_accomodation_publicreq_search_filters(GET, i)
				prw = PublicRequestWing.objects.filter(filters)
				for pw in prw:
					cpy = copy.deepcopy(search_obj)
					cpy.wing_introduction = pw.introduction
					cpy.wing_type = pw.wing_type
					cpy.wing_city = pw.city.name
					cpy.wing_start_date = pw.date_start
					cpy.wing_end_date = pw.date_end
					cpy.wing_capacity = pw.capacity
					search_list.objects.append(cpy)
			else:
				search_list.objects.append(search_obj)

		return search_list, count, start, end

	def search_accomodation(self, request, **kwargs):
		valid_time = getattr(settings, 'TOKEN_DISCONNECTED', 60)
		errors = self.validate_accomodation_search(request.GET)
		if len(errors) > 0:
			return self.create_response(request, {"errors": errors, "status":False}, response_class=HttpForbidden)
		#We have no problem with the given filters
		filters = self.make_accomodation_search_filters(request.GET)
		#Now, we have to search online user with the givern filters and ordering by score
		profiles = UserProfile.objects.filter(filters & Q(last_js__gte=time.time() - valid_time)).distinct().order_by('-search_score')
		#Now let's see if the profiles we got fit the sample, or we have to fill with offline
		if self.try_to_fit(profiles, request.GET):
			search_list, count, start, end = self.fill_domain_search_accomodation(profiles, request.GET)
		else:
			profiles_off = UserProfile.objects.filter(filters & Q(last_js__lt=time.time() - valid_time)).distinct().order_by('-search_score')
			search_list, count, start, end = self.fill_domain_search_accomodation([i for i in profiles] + [i for i in profiles_off], request.GET)

		if not isinstance(request.user, User):
			search_list.make_dirty()

		data = {}
		data['profiles'] = search_list.jsonable()
		data['count'] = count
		data['startResult'] = start
		data['endResult'] = end
		return self.create_response(request, {"data": data, "status":True}, response_class=HttpResponse)

	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			try:
				callback = getattr(self, view)
				response = callback(request, *args, **kwargs)
				return response
			except BadRequest, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR", "msg": e}]
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
					errors = [{"type": "INTERNAL_ERROR", "msg": e}]
					content['errors'] = errors
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
				else:
					ccontent = {}
					errors = [{"type": "INTERNAL_ERROR", "msg": e}]
					content['errors'] = errors
					content['status'] = False
					return self.create_response(request, content, response_class = HttpResponse)
			except Exception, e:
				content = {}
				errors = [{"type": "INTERNAL_ERROR", "msg": e}]
				content['errors'] = errors
				content['status'] = False
				return self.create_response(request, content, response_class = HttpResponse)

		return wrapper

class ContactResource(ModelResource):

	class Meta:
		object_class = UserProfile
		queryset = UserProfile.objects.all()
		detail_allowed_methods = []
		list_allowed_methods = ['get']
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		resource_name = 'contacts'


	def get_list(self, request, **kwargs):
		me = UserProfile.objects.get(user=request.user)
		result = {}
		result['items'] = []
		filters = (Q(notifications_receiver__sender=me)|Q(notifications_sender__receiver=me))&Q(active=True)
		if (request.GET.has_key('type') and request.GET['type'] == 'request'):
			filters = (filters) & ~Q(wing= None)
		contacts = UserProfile.objects.filter(filters).distinct().order_by('user__first_name', 'user__last_name')
		for i in contacts:
			aux = Contacts()
			aux.id = i.pk
			aux.name = i.user.first_name
			aux.lastName = i.user.last_name
			result['items'].append(aux.jsonable())
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


class PhotoCompletedResource(ModelResource):

	class Meta:
		object_class = Photos
		queryset = Photos.objects.all()
		allowed_methods = ['post']
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = Authentication()
		authorization = Authorization()
		always_return_data = True

	def post_list(self, request, **kwargs):
		#print '%s  %s' % ("POST", request.raw_post_data)
		encoded = request.raw_post_data
		print 'ENCODED PHOTO %s' % encoded
		POST= json.loads(encoded)
		if len(POST["results"]["images"]) != 2:
			return self.create_response(request, {"status":False, "errors":[{"type":"INVALID LENGTH"}]}, response_class=HttpResponse)
		try:
			i = 0;
			auth_token = request.GET['authToken']
			album_id = request.GET['album']
			photo_hash = request.GET['hash']
			for results in POST["results"]["images"]:
				url = results['s3_url']
				url = str.replace(str(url), 'http://', '//', 1)
				size = results['image_identifier']
				album = PhotoAlbums.objects.get(pk=album_id)
				apit = ApiToken.objects.get(token=auth_token)
				if (not blitline_token_is_authenticated(apit) or not (apit.user == album.author.user)):
					return self.create_response(request, {"status":False, "errors":[{"type":"FORBIDDEN"}]}, response_class=HttpResponse)

				if i == 0:
					final_photo= Photos.objects.create(author=UserProfile.objects.get(user=apit.user), album=album, photo_hash=photo_hash)
				if size == 'big':
					final_photo.big_url = url
				else:
					final_photo.thumb_url = url
				i = i + 1
			final_photo.save()
			self.reorder_album(album, final_photo)
		except Exception, e:
			return self.create_response(request, {"status":False, "errors": e}, response_class = HttpResponse)

		return self.create_response(request, {"status":True}, response_class = HttpResponse)

	def reorder_album(self, album, first):
		photos = Photos.objects.filter(album=album).order_by('ordering')
		aux = 2;
		for i in photos:
			if i != first:
				i.ordering = aux;
				aux = aux + 1
			else:
				i.ordering = 1
			i.save();

class PhotosResource(ModelResource):

	class Meta:
		object_class = Photos
		queryset = Photos.objects.all()
		detail_allowed_methods = ['delete', 'get']
		list_allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

	def delete_detail(self, request, **kwargs):
		id_photo = kwargs['pk']
		try:
			photo = Photos.objects.get(pk=id_photo)
			if photo.author == UserProfile.objects.get(user=request.user):
				photo.delete()
				return self.create_response(request, {"status":True}, response_class=HttpResponse)
			else:
				return self.create_response(request, {"status":False, "errors":[{"type":"FORBIDDEN"}]}, response_class=HttpResponse)
		except:
			return self.create_response(request, {"status":False, "errors":[{"type": 'INVALID_FIELD', "extras":['photo']}]}, response_class=HttpResponse)

	def get_detail(self, request, **kwargs):
		id_photo = kwargs['pk']
		try:
			photo = Photos.objects.get(pk=id_photo)
			return self.create_response(request, {"status":True, "data":{"id":photo.pk, "big_url": photo.big_url, "thumb_url": photo.thumb_url}}, response_class=HttpResponse)
		except:
			return self.create_response(request, {"status":False, "errors":[{"type": 'INVALID_FIELD', "extras":['photo']}]}, response_class=HttpResponse)

class AlbumsResource(ModelResource):

	class Meta:
		object_class = PhotoAlbums
		queryset = Photos.objects.all()
		detail_allowed_methods = ['put', 'get']
		list_allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

	def get_detail(self, request, **kwargs):
		id_album= kwargs['pk']
		try:
			album = PhotoAlbums.objects.get(pk=id_album)
			resp = {"id":album.pk, "name":album.name, "photos":[]}
			photos = Photos.objects.filter(album=album)
			for i in photos:
				cur_photo = {}
				cur_photo['id'] = i.pk
				cur_photo['big_url'] = i.big_url
				cur_photo['thumb_url'] = i.thumb_url
				resp['photos'].append(cur_photo)
			return self.create_response(request, {"status":True, "data":resp}, response_class=HttpResponse)
		except:
			return self.create_response(request, {"status":False, "errors":[{"type": 'INVALID_FIELD', "extras":['album']}]}, response_class=HttpResponse)

	def put_detail(self, request, **kwargs):
		id_album= kwargs['pk']
		PUT = json.loads(request.raw_post_data)
		if not self.validate_PUT(PUT):
			return self.create_response(request, {"status":False, "errors":[{"type": 'INVALID_FIELD', "extras":['photos']}]}, response_class=HttpResponse)
		try:
			album = PhotoAlbums.objects.get(pk=id_album)
			photos = Photos.objects.filter(album=album)
			idx = 1
			for i in PUT['photos']:
				if i in [j.pk for j in photos]:
					cur_photo = Photos.objects.get(pk=i)
					cur_photo.ordering = idx
					cur_photo.save()
					idx = idx + 1
			return self.create_response(request, {"status":True}, response_class=HttpResponse)
		except:
			return self.create_response(request, {"status":False, "errors":[{"type": 'INVALID_FIELD', "extras":['album']}]}, response_class=HttpResponse)

	def validate_PUT(self, PUT):
		if PUT.has_key('photos') and isinstance(PUT['photos'], list):
			return True
		return False





