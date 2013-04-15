#People API
import json
import re
import copy
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

from peoplewings.apps.people.models import UserProfile, UserLanguage, Language, University, SocialNetwork, UserSocialNetwork, InstantMessage, UserInstantMessage, UserProfileStudiedUniversity, Interests, Relationship, Reference
from peoplewings.apps.people.forms import UserProfileForm, UserLanguageForm, ReferenceForm
from people.domain import *
from peoplewings.global_vars import *
from peoplewings.apps.people.exceptions import *
from peoplewings.apps.ajax.utils import json_response, CamelCaseJSONSerializer
from peoplewings.apps.registration.api import AccountResource
from peoplewings.apps.registration.authentication import ApiTokenAuthentication, AnonymousApiTokenAuthentication
from peoplewings.apps.locations.api import CityResource
from peoplewings.apps.locations.models import Country, Region, City
from peoplewings.apps.wings.api import AccomodationsResource, WingResource
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.apps.wings.models import Accomodation, PublicRequestWing
from django.contrib.auth.models import User

class RelationshipResource(ModelResource):
	class Meta:
		object_class = UserProfile
		list_allowed_methods = ['get', 'post']
		detail_allowed_methods = ['put', 'delete']
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		include_resource_uri = True
		fields = ['avatar']

	def post_list(self, request, **kwargs):
		if 'profile_id' not in kwargs or kwargs['profile_id'] != 'me':
			return self.create_response(request, {"status" : False, "errors": [{"type":"AUTH_REQUIRED"}]}, response_class=HttpResponse)
		try:
			super(RelationshipResource, self).post_list(request, **kwargs)
		except IntegrityError:
			return self.create_response(request, {"status" : False, "errors": [{"type":"BAD_REQUEST"}]}, response_class=HttpResponse)
		except FriendYourselfError:
			return self.create_response(request, {"status" : False, "errors": [{"type":"BAD_REQUEST"}]}, response_class=HttpResponse)
		
		dic = {"status":True}
		return self.create_response(request, dic)

	@transaction.commit_on_success
	def obj_create(self, bundle, request=None, **kwargs):
		sender = UserProfile.objects.get(user=request.user)
		receiver = UserProfile.objects.get(pk=int(bundle.data['receiver'].split('/')[-1]))
		if sender.id == receiver.id: raise FriendYourselfError()
		if Relationship.objects.filter((Q(sender=sender) & Q(receiver=receiver)) | (Q(receiver=sender) & Q(sender=receiver))).exists():
			raise IntegrityError()
		rel = Relationship.objects.create(sender=sender, receiver=receiver, relationship_type="Pending")     
		return bundle

	def put_detail(self, request, **kwargs):
		try:
			super(RelationshipResource, self).put_detail(request, **kwargs)
		except CannotAcceptOrRejectError:
			return self.create_response(request, {"status" : False, "errors": [{"type":"BAD_REQUEST"}]}, response_class=HttpResponse)
		except InvalidAcceptRejectError:
			return self.create_response(request, {"status" : False, "errors": [{"type":"INVALID_FIELD", "extras":["type"]}]}, response_class=HttpResponse)
		
		deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
		deserialized = self.alter_deserialized_detail_data(request, deserialized)
		bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
		dic = {"status":True}
		return self.create_response(request, dic)        

	@transaction.commit_on_success
	def obj_update(self, bundle, request=None, **kwargs):
		receiver = UserProfile.objects.get(user=request.user)
		sender = UserProfile.objects.get(pk=int(kwargs['profile_id']))
		if not Relationship.objects.filter(sender=sender, receiver=receiver, relationship_type="Pending").exists(): 
			raise CannotAcceptOrRejectError()
		tipo = bundle.data['type']
		if tipo == "Accepted":
			rel = Relationship.objects.get(sender=sender, receiver=receiver)
			rel.relationship_type = tipo
			rel.save()
		elif tipo == "Rejected":
			Relationship.objects.get(sender=sender, receiver=receiver).delete()
		else:
			raise InvalidAcceptRejectError()
		return bundle

	def delete_detail(self, request, **kwargs):
		try:
			super(RelationshipResource, self).delete_detail(request, **kwargs)
		except ObjectDoesNotExist, e:
			return self.create_response(request, {"status" : False, "errors": [{"type":"BAD_REQUEST"}]}, response_class=HttpResponse)
		
		dic = {"status":True}
		return self.create_response(request, dic)  

	def obj_delete(self, request=None, **kwargs):
		receiver = UserProfile.objects.get(user=request.user)
		sender = UserProfile.objects.get(pk=int(kwargs['profile_id']))
		Relationship.objects.get((Q(sender=sender) & Q(receiver=receiver)) | (Q(receiver=sender) & Q(sender=receiver)), relationship_type="Accepted").delete()

	def get_list(self, request, **kwargs):
		up = UserProfile.objects.get(user=request.user)
		# miramos si el cliente quiere listar las invitaciones pendientes o los amigos
		status = request.GET['status']
		if status == 'friends':
			rels = Relationship.objects.filter(Q(sender=up) | Q(receiver=up), relationship_type="Accepted")
		elif status == 'pendings':
			rels = Relationship.objects.filter(Q(sender=up) | Q(receiver=up), relationship_type="Pending")
		else:
			return self.create_response(request, {"status" : False, "errors": [{"type":"INVALID_FIELD", "extras":["status"]}]}, response_class=HttpResponse)
		res = []
		for r in rels:
			if r.sender == up: bundle = self.build_bundle(obj=r.receiver, request=request)
			else: bundle = self.build_bundle(obj=r.sender, request=request)
			bundle = self.full_dehydrate(bundle)
			res.append(bundle)

		content = {}  
		content['status'] = True
		content['data'] = res
		return self.create_response(request, content, response_class=HttpResponse)

	def dehydrate(self, bundle):
		bundle.data['first_name'] = bundle.obj.user.first_name
		bundle.data['last_name'] = bundle.obj.user.last_name
		bundle.data['resource_uri'] = bundle.data['resource_uri'].replace('relationship', 'profiles')
		return bundle

	def alter_list_data_to_serialize(self, request, data):
		return data['objects']

class ReferenceResource(ModelResource):
	author = fields.ToOneField('peoplewings.apps.people.api.UserProfileResource', 'author', full=True, null=True)

	class Meta:
		object_class = Reference
		list_allowed_methods = ['get', 'post']
		#detail_allowed_methods = ['get']
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		include_resource_uri = True
		excludes = ['id']
		validation = FormValidation(form_class=ReferenceForm)
		
	def dehydrate_author(self, bundle):
		return_fields = ['avatar', 'first_name', 'last_name']
		res = {}
		for i in return_fields:
			res[i] = bundle.data['author'][i]
		return res

	def post_list(self, request, **kwargs):
		deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
		deserialized = self.alter_deserialized_detail_data(request, deserialized)
		bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
		self.is_valid(bundle)
		if bundle.errors:
			self.error_response(bundle.errors, request)

		try:
			super(ReferenceResource, self).post_list(request, **kwargs)
		except CommentYourselfError:
			return self.create_response(request, {"status" : False, "errors": [{"type":"BAD_REQUEST"}]}, response_class=HttpResponse)
		
		dic = {"status":True}
		return self.create_response(request, dic)

	@transaction.commit_on_success
	def obj_create(self, bundle, request=None, **kwargs):
		author = UserProfile.objects.get(user=request.user)
		commented = UserProfile.objects.get(pk=int(kwargs['profile_id']))
		if author.id == commented.id: raise CommentYourselfError()
		ref = Reference.objects.create(author=author, commented=commented, title=bundle.data['title'], text=bundle.data['text'], punctuation=bundle.data['punctuation'])     
		return bundle

	def get_list(self, request, **kwargs):
		up = UserProfile.objects.get(user=request.user)
		refs = Reference.objects.filter(commented=up)
		res = []
		for r in refs:
			bundle = self.build_bundle(obj=r, request=request)
			bundle = self.full_dehydrate(bundle)
			res.append(bundle)

		content = {}  
		content['status'] = True
		content['data'] = res
		return self.create_response(request, content, response_class=HttpResponse)

	def alter_list_data_to_serialize(self, request, data):
		return data['objects']

class InstantMessageResource(ModelResource):
	class Meta:
		object_class = InstantMessage
		queryset = InstantMessage.objects.all()
		allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

class UserInstantMessageResource(ModelResource):
	instant_message = fields.ToOneField(InstantMessageResource, 'instant_message', full=True)
	user_profile = fields.ToOneField('peoplewings.apps.people.api.UserProfileResource', 'user_profile')

	class Meta:
		object_class = UserInstantMessage
		queryset = UserInstantMessage.objects.all()
		allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

class SocialNetworkResource(ModelResource):
	class Meta:
		object_class = SocialNetwork
		queryset = SocialNetwork.objects.all()
		allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

class UserSocialNetworkResource(ModelResource):
	social_network = fields.ToOneField(SocialNetworkResource, 'social_network', full=True)
	user_profile = fields.ToOneField('peoplewings.apps.people.api.UserProfileResource', 'user_profile')

	class Meta:
		object_class = UserSocialNetwork
		queryset = UserSocialNetwork.objects.all()
		allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

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

class UserUniversityResource(ModelResource):
	university = fields.ToOneField(UniversityResource, 'university', full=True)
	user_profile = fields.ToOneField('peoplewings.apps.people.api.UserProfileResource', 'user_profile')

	class Meta:
		object_class = UserProfileStudiedUniversity
		queryset = UserProfileStudiedUniversity.objects.all()
		allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True

class LanguageResource(ModelResource):
	class Meta:
		object_class = Language
		resource_name = 'languages'
		queryset = Language.objects.all()
		list_allowed_methods = ['get']
		include_resource_uri = False
		fields = ['name']
		serializer = CamelCaseJSONSerializer(formats=['json'])
		#authentication = AnonymousApiTokenAuthentication()
		authorization = ReadOnlyAuthorization()
		always_return_data = True
		filtering = {
			"name": ['exact'],
		}

	def get_list(self, request, **kwargs):
		response = super(LanguageResource, self).get_list(request, **kwargs)
		data = json.loads(response.content)
		content = {}  
		content['status'] = True
		content['data'] = []
		for lang in data:
			content['data'].append(lang['name'])
		return self.create_response(request, content, response_class=HttpResponse)

	def alter_list_data_to_serialize(self, request, data):
		return data["objects"]


class UserLanguageResource(ModelResource):
	language = fields.ToOneField(LanguageResource, 'language', full=True)
	user_profile = fields.ToOneField('peoplewings.apps.people.api.UserProfileResource', 'user_profile')

	class Meta:
		object_class = UserLanguage
		queryset = UserLanguage.objects.all()
		allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		validation = FormValidation(form_class=UserLanguageForm)

class InterestsResource(ModelResource):
	class Meta:
		object_class = Interests
		queryset = Interests.objects.all()
		allowed_methods = []
		include_resource_uri = False
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = ApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		fields = ['gender']

class UserProfileResource(ModelResource):    

	class Meta:
		object_class = UserProfile
		queryset = UserProfile.objects.all()
		allowed_methods = ['get', 'put']
		include_resource_uri = True
		resource_name = 'profiles'
		serializer = CamelCaseJSONSerializer(formats=['json'])
		authentication = AnonymousApiTokenAuthentication()
		authorization = Authorization()
		always_return_data = True
		validation = FormValidation(form_class=UserProfileForm)

	def connected(self, user):
		state = 'OFF'
		token = ApiToken.objects.filter(user=user).order_by('-last_js')
		if len(token) > 0:
			state = token[0].is_user_connected()
		return state

	# funcion para trabajar con las wings de un profile. Por ejemplo, GET profiles/me/wings lista mis wings
	def prepend_urls(self):
		return [
			##/profiles/<profile_id>|me/accomodations/list
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/accomodations/list%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('accomodation_collection'), name="api_list_wings"),
			##/profiles/<profile_id>|me/accomodations/<accomodation_id> 
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/accomodations/(?P<wing_id>\d[\d/-]*)%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('accomodation_detail'), name="api_detail_wing"),
			# PREVIEW WING 34 OF PROFILE 2: GET /profiles/2/accomodations/34/preview
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\d[\d/-]*)/accomodations/(?P<wing_id>\d[\d/-]*)/preview%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('accomodation_detail'), name="api_detail_wing"),
			# PREVIEW ALL WINGS OF PROFILE 2: GET /profiles/2/accomodations/preview
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\d[\d/-]*)/accomodations/preview%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('accomodation_collection'), name="api_list_wings"),
			# VIEW ALL WINGS FOR EDDITING: GET /profiles/2/accomodations/preview
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\d[\d/-]*)/accomodations%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('accomodation_collection'), name="api_list_wings"),
			# GET THE NAMES, TYPES AND IDS OF ALL WINGS OF A USER: /profiles/<profile_id>/wings
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\d[\d/-]*)/wings%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('wing_collection'), name="api_list_wings"),

			# /profiles/<profile_id>|me/relationships/
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/relationships%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('relationship_collection'), name="api_list_relationships"),
			# /profiles/me/relationships/<profile_id>
			url(r"^(?P<resource_name>%s)/me/relationships/(?P<profile_id>\d[\d/-]*)%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('relationship_detail'), name="api_detail_relationships"),
			# /profiles/<profile_id>|me/references
			url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/references%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('reference_collection'), name="api_list_references"),
			# PREVIEW PROFILE: GET /profiles/2/preview
			url(r"^(?P<resource_name>%s)/(?P<pk>\d[\d/-]*)/preview%s$" % (self._meta.resource_name, trailing_slash()), 
				self.wrap_view('preview_profile'), name="api_detail_preview"),
		]

	def accomodation_collection(self, request, **kwargs):
		accomodation_resource = AccomodationsResource()
		return accomodation_resource.dispatch_list(request, **kwargs)  

	def accomodation_detail(self, request, **kwargs):
		accomodation_resource = AccomodationsResource()
		return accomodation_resource.dispatch_detail(request, **kwargs)

	def relationship_collection(self, request, **kwargs):
		rr = RelationshipResource()
		return rr.dispatch_list(request, **kwargs)  

	def relationship_detail(self, request, **kwargs):
		rr = RelationshipResource()
		return rr.dispatch_detail(request, **kwargs)

	def reference_collection(self, request, **kwargs):
		rr = ReferenceResource()
		return rr.dispatch_list(request, **kwargs)

	def preview_profile(self, request, **kwargs):
		return self.dispatch_detail(request, **kwargs)

	def wing_collection(self, request, **kwargs):
		wing_resource = WingResource()
		return wing_resource.dispatch_list(request, **kwargs)  

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
						#import pdb; pdb.set_trace()
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
						prof_obj.last_login_date = str(last.last_login)
					elif conn == "AFK":
						prof_obj.last_login_date = "AFK"
					else:
						prof_obj.last_login_date = "ON"					
					education= UserProfileStudiedUniversity.objects.filter(user_profile= prof)
					for i in education:
						prof_obj.education.append({"institution":i.university.name, "degree":i.degree})
					
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
					return self.create_response(request, {"status":True, "data": prof_obj.jsonable()}, response_class=HttpResponse)
					
					#Return
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
							prof_obj.education.append({"institution":i.university.name, "degree":i.degree})
						
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
							prof_obj.last_login['lat'] = last_login.lat
							prof_obj.last_login['lon'] = last_login.lon
							prof_obj.last_login['name'] = last_login.name
							prof_obj.last_login['region'] = last_login.region.name
							prof_obj.last_login['country'] = last_login.region.country.name

						prof_obj.last_name = prof.user.last_name
						prof_obj.religion = prof.religion
						prof_obj.show_birthday = 'F'
						return self.create_response(request, {"status":True, "data": prof_obj.jsonable()}, response_class=HttpResponse)
						
						#Return
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
		"""
		if POST.has_key('showBirthday'):
			if POST['showBirthday'] == "":
				not_empty['extras'].append('showBirthday')
			elif POST['showBirthday'] not in ['F', 'P', 'N']:
				invalid['extras'].append('showBirthday')
		else:
			field_req['extras'].append('showBirthday')
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
						if not i.has_key('snUsername') and isinstance(i['snUsername'], str):
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
						if not i.has_key('imUsername') and isinstance(i['imUsername'], str):
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
		else:
			field_req['extras'].append('civilState')

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
					if not (POST['hometown'].has_key('lat') and POST['hometown'].has_key('lon') and POST['hometown'].has_key('country') and POST['hometown'].has_key('region') and POST['hometown'].has_key('name')):
						invalid['extras'].append('hometown')

		if POST.has_key('current'):
			if not isinstance(POST['current'], dict):
				invalid['extras'].append('current')
			else:
				if len(POST['current'].keys()) != 0:
					if not (POST['current'].has_key('lat') and POST['current'].has_key('lon') and POST['current'].has_key('country') and POST['current'].has_key('region') and POST['current'].has_key('name')):
						invalid['extras'].append('current')

		if POST.has_key('otherLocations'):
			if not isinstance(POST.has_key('otherLocations'), list):
				for i in POST['otherLocations']:
					if isinstance(i, dict) and len(i.keys()) != 0:
						if not (i.has_key('lat') and i.has_key('lon') and i.has_key('country') and i.has_key('region') and i.has_key('name')):
							invalid['extras'].append('otherLocations')

		if POST.has_key('education'):
			if not isinstance(POST['education'], list):
				invalid['extras'].append('education')
			else:
				for i in POST['education']:
					if not isinstance(i, dict):
						if 'education' not in invalid['extras']:
							invalid['extras'].append('education')
					else:
						if not i.has_key('institution'):
							if 'education' not in invalid['extras']:
								invalid['extras'].append('education')
						else:
							if len(i['institution']) > 100:
								too_long['extras'].append('education')
						if not i.has_key('degree'):
							if 'education' not in invalid['extras']:
								invalid['extras'].append('education')
						else:
							if len(i['degree']) > 100:
								too_long['extras'].append('education')

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
			if len(POST['inspiredBy']) > 100:
				too_long['extras'].append('inspiredBy')					
		else:
			field_req['extras'].append('inspiredBy')

		if POST.has_key('otherPages'):
			if len(POST['otherPages']) > 100:
				too_long['extras'].append('otherPages')					
		else:
			field_req['extras'].append('otherPages')

		if POST.has_key('enjoyPeople'):
			if len(POST['enjoyPeople']) > 100:
				too_long['extras'].append('enjoyPeople')					
		else:
			field_req['extras'].append('enjoyPeople')

		if POST.has_key('gender'):
			if POST['gender'] not in ['Male', 'Female']:
				invalid['extras'].append('gender')
		else:
			field_req['extras'].append('gender')

		if POST.has_key('allAboutYou'):
			if len(POST['allAboutYou']) > 100:
				too_long['extras'].append('allAboutYou')				
		else:
			field_req['extras'].append('allAboutYou')

		if POST.has_key('movies'):
			if len(POST['movies']) > 100:
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
			if len(POST['religion']) > 100:
				too_long['extras'].append('religion')				
		else:
			field_req['extras'].append('religion')



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
			prof.current_city = City.objects.saveLocation(country=POST['current']['country'], region=POST['current']['region'], name=POST['current']['name'], lat=POST['current']['lat'], lon=POST['current']['lon'])
		if POST['hometown']:
			prof.hometown = City.objects.saveLocation(country=POST['hometown']['country'], region=POST['hometown']['region'], name=POST['hometown']['name'], lat=POST['hometown']['lat'], lon=POST['hometown']['lon'])
		prof.other_locations.clear()		
		if POST['otherLocations']:
			for i in POST['otherLocations']:
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
			if len(University.objects.filter(name=i['institution'])) > 0:
				univ = University.objects.get(name=i['institution'])
			else:
				univ = University.objects.create(name=i['institution'])
			UserProfileStudiedUniversity.objects.create(user_profile=prof, university=univ, degree=i['degree'])

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

	def validate_search(self, GET):
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

	def make_search_filters(self, GET):
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
				result = result & Q(wing__city__name__icontains=GET['wings'])
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
				result = result & Q(publicrequestwing__city__name__icontains=GET['wings'])
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

	def make_publicreq_search_filters(self, GET, prof):
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
		page_size=50
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

	def get_list(self, request, **kwargs):				
		errors = self.validate_search(request.GET)		
		if len(errors) > 0:
			return self.create_response(request, {"errors": errors, "status":False}, response_class=HttpForbidden)		
		#We have no problem with the given filters
		filters = self.make_search_filters(request.GET)	
		try:			
			search_list = SearchObjectManager()
			profiles = UserProfile.objects.filter(filters).distinct()		
			
			for i in profiles:
				search_obj = SearchObject()
				search_obj.profile_id = i.pk
				search_obj.ctrl_user = i.user
				search_obj.first_name = i.user.first_name
				search_obj.last_name = i.user.last_name
				search_obj.current = {"name": i.current_city.name, "region": i.current_city.region.name, "country": i.current_city.region.country.name}
				search_obj.avatar = i.medium_avatar
				search_obj.age = i.get_age()
				search_obj.online = self.connected(i.user)
				search_obj.reply_rate = i.reply_rate
				search_obj.reply_time = i.reply_time
				search_obj.languages = self.parse_languages(i)
				search_obj.all_about_you = i.all_about_you
				search_obj.date_joined = self.parse_date(str(i.user.date_joined))
				search_obj.ctrl_online =  self.connected(i.user) in ['ON', 'AFK']

				if request.GET['type'] == 'Applicant':										
					filters = self.make_publicreq_search_filters(request.GET, i)
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
		except Exception, e:
			return self.create_response(request, {"errors": [{"type": "INTERNAL_ERROR"}], "status":False}, response_class=HttpApplicationError)

		if not isinstance(request.user, User):
			search_list.make_dirty()

		data = self.paginate(search_list.jsonable(), request.GET)

		if isinstance(data, HttpResponse): return data
		return self.create_response(request, {"data": data, "status":True}, response_class=HttpResponse)	

	def full_dehydrate(self, bundle):				
		bundle = super(UserProfileResource, self).full_dehydrate(bundle)
		bundle.data['first_name'] = bundle.obj.user.first_name
		bundle.data['last_name'] = bundle.obj.user.last_name
		bundle.data['verified'] = 'XXX'
		#bundle.data['num_friends'] = Relationship.objects.filter(Q(sender=bundle.obj) | Q(receiver=bundle.obj), relationship_type='Accepted').count()
		bundle.data['num_friends'] = 'XXX'
		bundle.data['num_references'] = Reference.objects.filter(commented=bundle.obj).count()
		bundle.data['reply_rate'] = int(bundle.data['reply_rate'])
		bundle.data['reply_time'] = int(bundle.data['reply_time'])
		bundle.data['num_photos'] = 'XXX'
		bundle.data['age'] = bundle.obj.get_age()
		bundle.data['online'] = self.connected(bundle.obj.user)
		from datetime import timedelta
		d = timedelta(hours=1)
		online = ApiToken.objects.filter(user=bundle.obj.user, last__gte=date.today()-d).exists()
		if online: bundle.data['last_login_date'] = "ON"
		else: bundle.data['last_login_date'] = bundle.obj.user.last_login.strftime("%a %b %d %H:%M:%S %Y")

		if bundle.request.path not in (self.get_resource_uri(bundle), self.get_resource_uri(bundle)+"/preview"):
			# venimos de get_list => solamente devolver los campos requeridos
			bundle.data['pending'] = 'XXX'
			permitted_fields = ['first_name', 'last_name' , 'medium_avatar', 'blur_avatar', 'age', 'languages', 'occupation', 'all_about_you', 'current', 'verified', 'num_friends', 'num_references', 'pending', 'reply_rate', 'reply_time', 'resource_uri', 'online']
			
			for key, value in bundle.data.items():
				if key not in permitted_fields: del bundle.data[key]
			
			if 'lat' in bundle.data['current']: del bundle.data['current']['lat']
			if 'lon' in bundle.data['current']: del bundle.data['current']['lon']            

			if bundle.request.user.is_anonymous():
				# borroneo del nombre y el avatar
				"""
				from django.conf import settings as django_settings
				bundle.data['avatar'] = django_settings.ANONYMOUS_AVATAR
				"""
				bundle.data['avatar'] = bundle.data['blur_avatar']
				long_first = len(bundle.obj.user.first_name)
				long_last = len(bundle.obj.user.last_name)
				import string, random
				ran_name = [random.choice(string.ascii_lowercase) for n in xrange(long_first)]
				ran_last = [random.choice(string.ascii_lowercase) for n in xrange(long_last)]
				ran_name = "".join(ran_name)
				ran_last = "".join(ran_last)
				ran_name = ran_name.capitalize()
				ran_last = ran_last.capitalize()
				bundle.data['first_name'] = ran_name
				bundle.data['last_name'] = ran_last
			else:
				bundle.data['avatar'] = bundle.data['medium_avatar']
			del bundle.data['blur_avatar']
			del bundle.data['medium_avatar']
		else:

			# venimos de get_detail y ademas el usuario esta logueado
			del bundle.data['blur_avatar']
			del bundle.data['medium_avatar']
			del bundle.data['thumb_avatar']
			is_preview = bundle.request.path == self.get_resource_uri(bundle)+"/preview"
			if is_preview:
				del bundle.data['emails']
				del bundle.data['social_networks']
				del bundle.data['instant_messages']
				del bundle.data['phone']
				bundle.data['resource_uri'] += '/preview'

				if bundle.data['show_birthday'] == 'N':
					bundle.data['birthday'] = ""
				elif bundle.data['show_birthday'] == 'P':
					bday = str.split(str(bundle.data['birthday']),'-')
					bundle.data['birthday'] = bday[1] + "-" + bday[2]
				del bundle.data['show_birthday']
			else:
				bundle.data['birth_day'] = str(bundle.obj.birthday.day)
				bundle.data['birth_month'] = str(bundle.obj.birthday.month)
				bundle.data['birth_year'] = str(bundle.obj.birthday.year)
				del bundle.data['birthday']

		return bundle.data
	
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
