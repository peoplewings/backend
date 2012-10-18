#People API
from peoplewings.apps.people.models import UserProfile, UserLanguage, Language, University, SocialNetwork, UserSocialNetwork, InstantMessage, UserInstantMessage, UserProfileStudiedUniversity
import json
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpAccepted, HttpForbidden, HttpApplicationError, HttpApplicationError, HttpMethodNotAllowed
from tastypie.utils import dict_strip_unicode_keys, trailing_slash
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django import forms
from django.utils.cache import patch_cache_control
from django.core import serializers
from django.http import HttpResponse, Http404
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, InvalidPage

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.registration.api import AccountResource
from peoplewings.apps.people.forms import UserProfileForm, UserLanguageForm
from peoplewings.apps.registration.authentication import ApiTokenAuthentication, AnonymousApiTokenAuthentication
from peoplewings.global_vars import LANGUAGES_LEVEL_CHOICES_KEYS
from peoplewings.apps.locations.api import CityResource
from peoplewings.apps.locations.models import Country, Region, City
from peoplewings.apps.wings.api import AccomodationsResource
from datetime import date

from pprint import pprint

import re

from django.db.models import Q

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
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            "name": ['exact'],
        }


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
        """
        filtering = {
            "level": ['exact'],
            "language": ALL_WITH_RELATIONS,
        }
        """


class UserProfileResource(ModelResource):    
    user = fields.ToOneField(AccountResource, 'user')

    languages = fields.ToManyField(LanguageResource, 'languages', full=True)
    #through_query = lambda bundle: UserLanguage.objects.filter(user_profile=bundle.obj)
    #userlanguages = fields.ToManyField(UserLanguageResource, attribute=through_query, full=True)

    education = fields.ToManyField(UniversityResource, 'universities', full=True)
    social_networks = fields.ToManyField(SocialNetworkResource, 'social_networks', full=True)
    instant_messages = fields.ToManyField(InstantMessageResource, 'instant_messages', full=True)
    current = fields.ToOneField(CityResource, 'current_city', full=True, null=True)
    hometown = fields.ToOneField(CityResource, 'hometown', full=True, null=True)
    other_locations = fields.ToManyField(CityResource, 'other_locations', full=True, null=True)

    class Meta:
        object_class = UserProfile
        queryset = UserProfile.objects.all()
        allowed_methods = ['get', 'post', 'put']
        include_resource_uri = False
        resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = AnonymousApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserProfileForm)
        filtering = {
            "age": ['range'],
            'gender':['in'],
            'languages':ALL_WITH_RELATIONS,
            #'userlanguages': ALL_WITH_RELATIONS,
        }

    def normalize_query(self, query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
        ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
            and grouping quoted words together.
            Example:
            
            >>> normalize_query('  some random  words "with   quotes  " and   spaces')
            ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
        
        '''
        return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

    def get_query(self, query_string, search_fields):
        ''' Returns a query, that is a combination of Q objects. That combination
            aims to search keywords within a model by testing the given search fields.
        
        '''
        query = None # Query to search for every search term        
        terms = self.normalize_query(query_string)
        for term in terms:
            or_query = None # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__icontains" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query
        return query

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(UserProfileResource, self).apply_filters(request, applicable_filters)

        query = request.GET.get('userlanguage__level', None)
        if query:
            entry_query = self.get_query(query, ['userlanguage__level'])
            if request.GET.get('languages__name', None): 
                base_object_list = base_object_list.filter(entry_query, userlanguage__language__name=request.GET.get('languages__name', None)).distinct()
            else:
                base_object_list = base_object_list.filter(entry_query).distinct()


        wing_filter = {}

        ds = None
        de = None

        if 'date_start__gte' in request.GET.keys():
            ds = request.GET['date_start__gte']

        if 'date_end__lte' in request.GET.keys():
            de = request.GET['date_end__lte']

        for k, v in request.GET.items():
            #print "insert key ", k, " with value ", v
            if k != 'date_start__gte' and k != 'date_end__lte': wing_filter[k] = v            

        ar = AccomodationsResource()
        wing_filter_2 = ar.build_filters(wing_filter)

        #for i in wing_filter_2: print i
        if len(wing_filter_2) > 0:
            accomodation_list = ar.apply_filters(request, wing_filter_2)

            if ds is not None:
                accomodation_list = accomodation_list.filter(
                    Q(date_start__gte=ds) | Q(date_start__isnull=True)
                )
            if de is not None:
                accomodation_list = accomodation_list.filter( 
                    Q(date_end__lte=de) | Q(date_end__isnull=True)
                )

            base_object_list = base_object_list.filter(wing__in=accomodation_list).distinct()

        paginator = Paginator(base_object_list, 10)
        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        return page

    # funcion para trabajar con las wings de un profile. Por ejemplo, GET profiles/me/wings lista mis wings
    def prepend_urls(self):
        return [
            ##/profiles/<profile_id>|me/accomodations/
            url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/accomodations%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('accomodation_collection'), name="api_list_wings"), 
            ##/profiles/<profile_id>|me/accomodations/<accomodation_id> 
            url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/accomodations/(?P<wing_id>\w[\w/-]*)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('accomodation_detail'), name="api_detail_wing"),
        ]

    def accomodation_collection(self, request, **kwargs):
        accomodation_resource = AccomodationsResource()
        return accomodation_resource.dispatch_list(request, **kwargs)  


    def accomodation_detail(self, request, **kwargs):
        accomodation_resource = AccomodationsResource()
        return accomodation_resource.dispatch_detail(request, **kwargs)

    
    #funcion llamada en el GET y que ha de devolver un objeto JSON con los idiomas hablados por el usuario
    def dehydrate_languages(self, bundle):
        for i in bundle.data['languages']: 
            # i = {id: id_language, name:'Spanish'}
            lang = i.obj
            ul = UserLanguage.objects.get(language=lang, user_profile=bundle.obj)
            i.data['level'] = ul.level
            i.data.pop('id')
        return bundle.data['languages']

    def dehydrate_education(self, bundle):
        for i in bundle.data['education']: 
            # i = {id: id_university, name:'University of Reading'}
            uni = i.obj
            upu = UserProfileStudiedUniversity.objects.get(university=uni, user_profile=bundle.obj)
            i.data['degree'] = upu.degree
            i.data.pop('id')
        return bundle.data['education']

    def dehydrate_social_networks(self, bundle):
        for i in bundle.data['social_networks']: 
            # i = {id: id_social_networks, name:'Facebook'}
            sn = i.obj
            usn = UserSocialNetwork.objects.get(social_network=sn, user_profile=bundle.obj)
            i.data['username'] = usn.social_network_username
            i.data.pop('id')
        return bundle.data['social_networks']

    def dehydrate_instant_messages(self, bundle):
        for i in bundle.data['instant_messages']: 
            # i = {id: id_instant_message, name:'Whatsapp'}
            im = i.obj
            uim = UserInstantMessage.objects.get(instant_message=im, user_profile=bundle.obj)
            i.data['username'] = uim.instant_message_username
            i.data.pop('id')
        return bundle.data['instant_messages']

    def dehydrate_current(self, bundle):
        if bundle.data['current'] is None: return {} 
        city = bundle.data['current'].obj
        region = city.region
        country = region.country
        bundle.data['current'] = {}
        bundle.data['current']['city'] = city.name
        bundle.data['current']['region'] = region.name
        bundle.data['current']['country'] = country.name
        return bundle.data['current']

    def dehydrate_hometown(self, bundle):
        if bundle.data['hometown'] is None: return {} 
        city = bundle.data['hometown'].obj
        region = city.region
        country = region.country
        bundle.data['hometown'] = {}
        bundle.data['hometown']['city'] = city.name
        bundle.data['hometown']['region'] = region.name
        bundle.data['hometown']['country'] = country.name
        return bundle.data['hometown']

    def dehydrate_other_locations(self, bundle):
        for i in bundle.data['other_locations']: 
            # tenemos: i.data = {id: id_city, lat, lon, name, resource_uri, short_name}
            # queremos: i.data = {city: nombre_city, region: nombre_region, country: nombre_country}
            city = i.obj
            i.data = {}
            region = city.region
            country = region.country
            i.data['city'] = city.name
            i.data['region'] = region.name
            i.data['country'] = country.name
        return bundle.data['other_locations']
    
    def apply_authorization_limits(self, request, object_list=None):
        if request.user.is_anonymous() and request.method not in ('GET'):
            return self.create_response(request, {"msg":"Error: anonymous users can only view profiles.", "status":False, "code":413}, response_class=HttpForbidden)
        elif not request.user.is_anonymous() and request.method not in ('GET'):
            return object_list.filter(user=request.user)
        return object_list

    def get_age(self, birthday):
        today = date.today()
        age = today.year - birthday.year
        if today.month < birthday.month or (today.month == birthday.month and today.day < birthday.day): age -= 1
        return age

    def get_detail(self, request, **kwargs):
        if request.user.is_anonymous(): return self.create_response(request, {"msg":"Error: operation not allowed", "code":413, "status":False}, response_class=HttpForbidden)
        #mostrar_para_update = kwargs['pk'] == 'me'
        #if mostrar_para_update: kwargs['pk'] = UserProfile.objects.get(user=request.user).id
        if kwargs['pk'] == 'me': kwargs['pk'] = UserProfile.objects.get(user=request.user).id
        a = super(UserProfileResource, self).get_detail(request, **kwargs)
        data = json.loads(a.content)
        """
        if mostrar_para_update:
            if data['show_birthday'] == 'P': del data['BYear']
        elif data['show_birthday'] == 'N': 
            del data['BYear']
            del data['BMonth']
            del data['BDay']
        """
        content = {}  
        content['msg'] = 'Profile retrieved successfully.'      
        content['status'] = True
        content['code'] = 200
        content['data'] = data
        return self.create_response(request, content, response_class=HttpResponse)
        """
        result = UserProfile.objects.get(pk=kwargs['pk'])
        bundle = self.build_bundle(obj=result, request=request)
        updated_bundle = self.dehydrate(bundle)
        updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        return self.create_response(request,{"msg":"Get OK.", "status":True, "code":200, "data":bundle.obj.__dict__})
        """

    @transaction.commit_on_success
    def put_detail(self, request, **kwargs):
        if request.user.is_anonymous(): 
            return self.create_response(request, {"msg":"Error: anonymous users have no profile.", "status":False, "code":413}, response_class=HttpForbidden)

        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)

        up = UserProfile.objects.get(user=request.user)
        self.is_valid(bundle, request)
        if bundle.errors:
            self.error_response(bundle.errors, request)

        if 'languages' in bundle.data:
            UserLanguage.objects.filter(user_profile_id=up.id).delete()
            for lang in bundle.data['languages']:
                UserLanguage.objects.create(user_profile_id=up.id, language_id=Language.objects.get(name=lang['name']).id, level=lang['level'])
            bundle.data.pop('languages')
        
        if 'education' in bundle.data:
            UserProfileStudiedUniversity.objects.filter(user_profile_id=up.id).delete()
            for e in bundle.data['education']:
                uni, b = University.objects.create(name=e['name'])
                UserProfileStudiedUniversity.objects.get_or_create(user_profile_id=up.id, university_id=uni.id, degree=e['degree'])
            bundle.data.pop('education')

        if 'instant_messages' in bundle.data:
            UserInstantMessage.objects.filter(user_profile_id=up.id).delete()
            for im in bundle.data['instant_messages']:
                UserInstantMessage.objects.create(user_profile_id=up.id, instant_message_id=InstantMessage.objects.get(name=im['name']).id, instant_message_username=im['username'])
            bundle.data.pop('instant_messages')

        if 'social_networks' in bundle.data:
            UserSocialNetwork.objects.filter(user_profile_id=up.id).delete()
            for sn in bundle.data['social_networks']:
                UserSocialNetwork.objects.create(user_profile_id=up.id, social_network_id=SocialNetwork.objects.get(name=sn['name']).id, social_network_username=sn['username'])
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

        forbidden_fields_update = ['avatar', 'id', 'user']
        not_empty_fields = ['pw_state', "name_to_show", "gender"]

        for i in bundle.data:
            if hasattr(up, i) and i not in forbidden_fields_update: setattr(up, i, bundle.data.get(i))
        up.age = self.get_age(up.birthday)
        #if up.age < 18: return self.create_response(request, {"msg":"Error: age under 18.", "code":410, "status":False}, response_class=HttpForbidden)
        up.save()

        updated_bundle = self.dehydrate(bundle)
        updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        return self.create_response(request,{"msg":"Your profile has been successfully updated.", "code":200, "status":True}, response_class=HttpAccepted) 
    
    def post_list(self, request, **kwargs):
        return self.create_response(request, {"msg":"Error: operation not allowed.", "code":413, "status":False}, response_class=HttpForbidden)

    def put_list(self, request, **kwargs):
        return self.create_response(request, {"msg":"Error: operation not allowed.", "code":413, "status":False}, response_class=HttpForbidden)

    def get_list(self, request, **kwargs):
        response = super(UserProfileResource, self).get_list(request, **kwargs)
        data = json.loads(response.content)
        content = {}  
        content['msg'] = 'Profiles retrieved successfully.'      
        content['status'] = True
        content['code'] = 200
        content['data'] = data
        return self.create_response(request, content, response_class=HttpResponse)

    def full_dehydrate(self, bundle):
        bundle = super(UserProfileResource, self).full_dehydrate(bundle)
        bundle.data['BDay'] = bundle.obj.birthday.day
        bundle.data['BMonth'] = bundle.obj.birthday.month
        bundle.data['BYear'] = bundle.obj.birthday.year
        if bundle.request.user.is_anonymous():
            bundle.data['avatar'] = 'fake_' + bundle.data['avatar']
            bundle.data['name_to_show'] = 'fake_' + bundle.data['name_to_show']
        return bundle.data
    
    """
    def dehydrate(self, bundle):
        
        if bundle.request.method == 'PUT':
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 204
            bundle.data['msg'] = 'Update OK'
            self.method = None
            return bundle   
        elif bundle.request.method == 'GET':
            b = bundle.data
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 204
            bundle.data['msg'] = 'Update OK'
            bundle.data['data'] = b
            return bundle
        return super(UserProfileResource, self).dehydrate(bundle)
    """
    
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
                errors = {}
                errors['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                errors['msg'] = "Error in some fields"
                errors['errors'] = json.loads(e.messages)                
                content['code'] = 410
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                errors['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
                content['error'] = errors
                return self.create_response(request, content, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    errors['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpUnauthorized)):
                    content = {}
                    errors = {}
                    errors['msg'] = "Unauthorized"                               
                    content['code'] = 413
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpApplicationError)):
                    content = {}
                    errors = {}
                    errors['msg'] = "Can't logout"                               
                    content['code'] = 400
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
                else:               
                    content = {}
                    errors = {}
                    errors['msg'] = "Error in some fields"               
                    content['code'] = 400
                    content['status'] = False
                    content['error'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
            except Exception, e:
                return self._handle_500(request, e)

        return wrapper


