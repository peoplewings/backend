#People API
from peoplewings.apps.people.models import UserProfile, UserLanguage, Language, University, SocialNetwork, UserSocialNetwork, InstantMessage, UserInstantMessage, UserProfileStudiedUniversity
import json
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpAccepted, HttpForbidden
from tastypie.utils import dict_strip_unicode_keys
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.utils.cache import patch_cache_control

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer

from django.core import serializers
from django.http import HttpResponse
from peoplewings.apps.registration.api import AccountResource
from peoplewings.apps.people.forms import UserProfileForm
from peoplewings.apps.people.authorization import ProfileAuthorization
from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.global_vars import LANGUAGES_LEVEL_CHOICES_KEYS

from peoplewings.apps.locations.api import CityResource
from peoplewings.apps.locations.models import Country, Region, City

import pprint

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
    user_profile = fields.ToOneField('apps.people.api.UserProfileResource', 'user_profile')

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
    user_profile = fields.ToOneField('apps.people.api.UserProfileResource', 'user_profile')

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
        allowed_methods = []
        include_resource_uri = False
        #resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True

class UserUniversityResource(ModelResource):    
    university = fields.ToOneField(UniversityResource, 'university', full=True)
    user_profile = fields.ToOneField('apps.people.api.UserProfileResource', 'user_profile')

    class Meta:
        object_class = UserProfileStudiedUniversity
        queryset = UserProfileStudiedUniversity.objects.all()
        allowed_methods = []
        include_resource_uri = False
        #resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True

class LanguageResource(ModelResource):
    class Meta:
        object_class = Language
        queryset = Language.objects.all()
        allowed_methods = []
        include_resource_uri = False
        #resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=UserProfileForm)


class UserLanguageResource(ModelResource):    
    language = fields.ToOneField(LanguageResource, 'language', full=True)
    user_profile = fields.ToOneField('apps.people.api.UserProfileResource', 'user_profile')

    class Meta:
        object_class = UserLanguage
        queryset = UserLanguage.objects.all()
        allowed_methods = []
        include_resource_uri = False
        #resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=UserProfileForm)

class UserProfileResource(ModelResource):    
    user = fields.ToOneField(AccountResource, 'user')
    languages = fields.ToManyField(LanguageResource, 'languages', full=True)
    education = fields.ToManyField(UniversityResource, 'universities', full=True)
    social_networks = fields.ToManyField(SocialNetworkResource, 'social_networks', full=True)
    instant_messages = fields.ToManyField(InstantMessageResource, 'instant_messages', full=True)
    current = fields.ToOneField(CityResource, 'current_city', full=True, null=True)
    hometown = fields.ToOneField(CityResource, 'hometown', full=True, null=True)
    other_locations = fields.ToManyField(CityResource, 'other_locations', full=True, null=True)
    method = None
    class Meta:
        object_class = UserProfile
        queryset = UserProfile.objects.all()
        allowed_methods = ['get', 'post']
        include_resource_uri = False
        resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserProfileForm)
        ordering = ['social_networks', 'instant_messages']

    #funcion llamada en el GET y que ha de devolver un objeto JSON con los idiomas hablados por el usuario
    def dehydrate_languages(self, bundle):
        #print "dehydrate languages "
        #id_user = bundle.data['id']
        id_user = UserProfile.objects.get(user_id=bundle.request.user.id).id
        up = UserProfile.objects.get(pk=id_user)

        for i in bundle.data['languages']: 
            # i = {id: id_language, name:'Spanish'}
            lang = Language.objects.get(pk=i.data['id'])
            ul = UserLanguage.objects.get(language=lang, user_profile=up)
            i.data['level'] = ul.level
            i.data.pop('id')
        return bundle.data['languages']

    def dehydrate_education(self, bundle):
        #print "dehydrate education "
        #id_user = bundle.data['id']
        id_user = UserProfile.objects.get(user_id=bundle.request.user.id).id
        up = UserProfile.objects.get(pk=id_user)

        for i in bundle.data['education']: 
            # i = {id: id_university, name:'University of Reading'}
            uni = University.objects.get(pk=i.data['id'])
            upu = UserProfileStudiedUniversity.objects.get(university=uni, user_profile=up)
            i.data['degree'] = upu.degree
            i.data.pop('id')
        return bundle.data['education']

    def dehydrate_social_networks(self, bundle):
        #print "dehydrate social_network "
        #id_user = bundle.data['id']
        id_user = UserProfile.objects.get(user_id=bundle.request.user.id).id
        up = UserProfile.objects.get(pk=id_user)

        for i in bundle.data['social_networks']: 
            # i = {id: id_social_networks, name:'Facebook'}
            sn = SocialNetwork.objects.get(pk=i.data['id'])
            usn = UserSocialNetwork.objects.get(social_network=sn, user_profile=up)
            i.data['username'] = usn.social_network_username
            i.data.pop('id')
        return bundle.data['social_networks']

    def dehydrate_instant_messages(self, bundle):
        #print "dehydrate instant_message "
        #id_user = bundle.data['id']
        id_user = UserProfile.objects.get(user_id=bundle.request.user.id).id
        up = UserProfile.objects.get(pk=id_user)

        for i in bundle.data['instant_messages']: 
            # i = {id: id_instant_message, name:'Whatsapp'}
            im = InstantMessage.objects.get(pk=i.data['id'])
            uim = UserInstantMessage.objects.get(instant_message=im, user_profile=up)
            i.data['username'] = uim.instant_message_username
            i.data.pop('id')
        return bundle.data['instant_messages']

    def dehydrate_current(self, bundle):
        id_user = UserProfile.objects.get(user_id=bundle.request.user.id).id
        up = UserProfile.objects.get(pk=id_user)

        city = up.current_city
        if city is None: return {}
        region = city.region
        country = region.country
        bundle.data['current'] = {}
        bundle.data['current']['city'] = city.name
        bundle.data['current']['region'] = region.name
        bundle.data['current']['country'] = country.name
        return bundle.data['current']

    def dehydrate_hometown(self, bundle):
        id_user = UserProfile.objects.get(user_id=bundle.request.user.id).id
        up = UserProfile.objects.get(pk=id_user)

        city = up.hometown
        if city is None: return {}
        region = city.region
        country = region.country
        bundle.data['hometown'] = {}
        bundle.data['hometown']['city'] = city.name
        bundle.data['hometown']['region'] = region.name
        bundle.data['hometown']['country'] = country.name
        return bundle.data['hometown']

    def dehydrate_other_locations(self, bundle):
        #print "dehydrate instant_message "
        #id_user = bundle.data['id']
        id_user = UserProfile.objects.get(user_id=bundle.request.user.id).id
        up = UserProfile.objects.get(pk=id_user)

        for i in bundle.data['other_locations']: 
            # tenemos: i.data = {id: id_city, lat, lon, name, resource_uri, short_name}
            # queremos: i.data = {city: nombre_city, region: nombre_region, country: nombre_country}
            city = City.objects.get(pk=i.data['id'])
            i.data = {}
            region = city.region
            country = region.country
            i.data['city'] = city.name
            i.data['region'] = region.name
            i.data['country'] = country.name
        return bundle.data['other_locations']

    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('GET'):
            if 'from' in request.GET and 'to' in request.GET:
                initial = request.GET['from']
                final = request.GET['to']
                #initial = request.META['HTTP_FROM']
                #final = request.META['HTTP_TO']
                return object_list.all()[initial:final]
            elif 'pk' in request.GET: 
                return object_list.filter(pk=request.GET['pk'])
            else: 
                return object_list.filter(user=request.user)

    @transaction.commit_on_success
    def post_detail(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)       
        up = UserProfile.objects.get(user=request.user)

        if 'languages' in bundle.data:
            UserLanguage.objects.filter(user_profile_id=up.id).delete()
            for lang in bundle.data['languages']:
                #if lang['level'] not in LANGUAGES_LEVEL_CHOICES_KEYS: raise Exception("Incorrect level: it doesn't exist!!")
                UserLanguage.objects.get_or_create(user_profile_id=up.id, language_id=Language.objects.get(name=lang['name']).id, level=lang['level'])
            bundle.data.pop('languages')
        
        if 'education' in bundle.data:
            UserProfileStudiedUniversity.objects.filter(user_profile_id=up.id).delete()
            for e in bundle.data['education']:
                uni, b = University.objects.get_or_create(name=e['university'])
                UserProfileStudiedUniversity.objects.get_or_create(user_profile_id=up.id, university_id=uni.id, degree=e['degree'])
            bundle.data.pop('education')

        if 'instant_messages' in bundle.data:
            UserInstantMessage.objects.filter(user_profile_id=up.id).delete()
            for im in bundle.data['instant_messages']:
                UserInstantMessage.objects.get_or_create(user_profile_id=up.id, instant_message_id=InstantMessage.objects.get(name=im['instant_message']).id, instant_message_username=im['username'])
            bundle.data.pop('instant_messages')

        if 'social_networks' in bundle.data:
            UserSocialNetwork.objects.filter(user_profile_id=up.id).delete()
            for sn in bundle.data['social_networks']:
                UserSocialNetwork.objects.get_or_create(user_profile_id=up.id, social_network_id=SocialNetwork.objects.get(name=sn['social_network']).id, social_network_username=sn['username'])
            bundle.data.pop('social_networks')

        if 'current' in bundle.data:
            if 'city' in bundle.data['current'] and 'region' in bundle.data['current'] and 'country' in bundle.data['current']:
                country, b = Country.objects.get_or_create(name=bundle.data['current']['country'])
                region, b = Region.objects.get_or_create(name=bundle.data['current']['region'], country=country)
                city, b = City.objects.get_or_create(name=bundle.data['current']['city'], region=region)
                up.current_city = city
            else:
                up.current_city = None
            bundle.data.pop('current')

        if 'hometown' in bundle.data:
            if 'city' in bundle.data['hometown'] and 'region' in bundle.data['hometown'] and 'country' in bundle.data['hometown']:
                country, b = Country.objects.get_or_create(name=bundle.data['hometown']['country'])
                region, b = Region.objects.get_or_create(name=bundle.data['hometown']['region'], country=country)
                city, b = City.objects.get_or_create(name=bundle.data['hometown']['city'], region=region)
                up.hometown = city
            else:
                up.hometown = None
            bundle.data.pop('hometown')

        if 'other_locations' in bundle.data:
            up.other_locations = []
            for ol in bundle.data['other_locations']:
                country, b = Country.objects.get_or_create(name=ol['country'])
                region, b = Region.objects.get_or_create(name=ol['region'], country=country)
                city, b = City.objects.get_or_create(name=ol['city'], region=region)
                up.other_locations.add(city)
            bundle.data.pop('other_locations')

        for i in bundle.data:
            if hasattr(up, i): setattr(up, i, bundle.data.get(i))
        up.save()
        self.method = 'POST'
        updated_bundle = self.dehydrate(bundle)
        updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        return self.create_response(request, updated_bundle, response_class=HttpAccepted) 
    
    def post_list(self, request, **kwargs):
        print "no autorizado el post_list"
        return self.create_response(request, {}, response_class=HttpForbidden)

    def dehydrate(self, bundle):
        if self.method:
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 204
            bundle.data['data'] = 'Updated'
            self.method = None
            return bundle   
        else:
             return super(UserProfileResource, self).dehydrate(bundle)  
    
    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):    
            try:
                #print kwargs
                #print request
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)
                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                return response
            except BadRequest, e:
                return HttpBadRequest({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "errors": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "errors": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpUnauthorized)):
                    bundle = {"code": 401, "status": False, "errors":"Unauthorized"}
                    return self.create_response(request, bundle, response_class = HttpUnauthorized)
                if (isinstance(e.response, HttpApplicationError)):
                    bundle = {"code": 401, "status": False, "errors":"Error"}
                    return self.create_response(request, bundle, response_class = HttpApplicationError)          
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper


