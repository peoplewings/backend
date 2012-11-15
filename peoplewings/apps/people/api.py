#People API
import json
import re
from datetime import date, datetime
from pprint import pprint
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
from django.db.models import Q
from django.forms import ValidationError
from django import forms
from django.utils.cache import patch_cache_control
from django.core import serializers
from django.http import HttpResponse, Http404
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, InvalidPage

from peoplewings.apps.people.models import UserProfile, UserLanguage, Language, University, SocialNetwork, UserSocialNetwork, InstantMessage, UserInstantMessage, UserProfileStudiedUniversity, Interests, Relationship
from peoplewings.apps.people.forms import UserProfileForm, UserLanguageForm
from peoplewings.apps.people.exceptions import FriendYourselfError, CannotAcceptOrRejectError, InvalidAcceptRejectError
from peoplewings.apps.ajax.utils import json_response, CamelCaseJSONSerializer
from peoplewings.apps.registration.api import AccountResource
from peoplewings.apps.registration.authentication import ApiTokenAuthentication, AnonymousApiTokenAuthentication
from peoplewings.apps.locations.api import CityResource
from peoplewings.apps.locations.models import Country, Region, City
from peoplewings.apps.wings.api import AccomodationsResource
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.apps.wings.models import Accomodation

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
            return self.create_response(request, {"code" : 401, "status" : False, "msg": "Unauthorized"}, response_class=HttpForbidden)
        try:
            super(RelationshipResource, self).post_list(request, **kwargs)
        except IntegrityError:
            return self.create_response(request, {"msg":"The relationship already exists." ,"code" : 410, "status" : False}, response_class=HttpForbidden)
        except FriendYourselfError:
            return self.create_response(request, {"msg":"Cannot be friend of yourself." ,"code" : 410, "status" : False}, response_class=HttpForbidden)
        
        dic = {"msg":"Invitation sent. Pending to be accepted.", "status":True, "code":200}
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
            return self.create_response(request, {"msg":"That relationship is not pending." ,"code" : 410, "status" : False}, response_class=HttpForbidden)
        except InvalidAcceptRejectError:
            return self.create_response(request, {"msg":"Invalid type." ,"code" : 410, "status" : False}, response_class=HttpForbidden)
        
        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        tipo = bundle.data['type']
        if tipo == "Accepted": txt = "Invitation accepted."
        else: txt = "Invitation rejected."
        dic = {"msg":txt, "status":True, "code":200}
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
            return self.create_response(request, {"msg":"That relationship doesn't exist." ,"code" : 410, "status" : False}, response_class=HttpForbidden)
        
        dic = {"msg":"You are not friend of that user anymore.", "status":True, "code":200}
        return self.create_response(request, dic)  

    def obj_delete(self, request=None, **kwargs):
        receiver = UserProfile.objects.get(user=request.user)
        sender = UserProfile.objects.get(pk=int(kwargs['profile_id']))
        Relationship.objects.get((Q(sender=sender) & Q(receiver=receiver)) | (Q(receiver=sender) & Q(sender=receiver)), relationship_type="Accepted").delete()

    """
    def obj_get_list(self, request=None, **kwargs):
        u = request.user
        rels = Relationship.objects.filter(Q(sender=u) | Q(receiver=u))
        res = []
        for r in rels:
            if r.sender == u: res.append(r.receiver)
            else: res.append(r.sender)

        return res
    """
    def get_list(self, request, **kwargs):
        up = UserProfile.objects.get(user=request.user)
        # miramos si el cliente quiere listar las invitaciones pendientes o los amigos
        status = request.GET['status']
        if status == 'friends':
            rels = Relationship.objects.filter(Q(sender=up) | Q(receiver=up), relationship_type="Accepted")
        elif status == 'pendings':
            rels = Relationship.objects.filter(Q(sender=up) | Q(receiver=up), relationship_type="Pending")
        else:
            return self.create_response(request, {'msg':"Status not valid, must be either 'friends' or 'pendings' ", 'status':False, 'code':200}, response_class=HttpResponse)
        res = []
        for r in rels:
            if r.sender == up: bundle = self.build_bundle(obj=r.receiver, request=request)
            else: bundle = self.build_bundle(obj=r.sender, request=request)
            bundle = self.full_dehydrate(bundle)
            res.append(bundle)

        content = {}  
        if status == 'friends': content['msg'] = 'Friends retrieved successfully.'
        else: content['msg'] = 'Invitations retrieved successfully.'
        content['status'] = True
        content['code'] = 200
        content['data'] = res
        return self.create_response(request, content, response_class=HttpResponse)

    def dehydrate(self, bundle):
        bundle.data['first_name'] = bundle.obj.user.first_name
        bundle.data['last_name'] = bundle.obj.user.last_name
        bundle.data['resource_uri'] = bundle.data['resource_uri'].replace('relationship', 'profiles')
        return bundle

    """
    def apply_authorization_limits(self, request, object_list=None):
        return object_list.filter(Q(sender=request.user) | Q(receiver=request.user))
    """

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
        content['msg'] = 'Languages retrieved successfully.'      
        content['status'] = True
        content['code'] = 200
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
        """
        filtering = {
            "level": ['exact'],
            "language": ALL_WITH_RELATIONS,
        }
        """
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
    user = fields.ToOneField(AccountResource, 'user')

    languages = fields.ToManyField(LanguageResource, 'languages', full=True)
    #through_query = lambda bundle: UserLanguage.objects.filter(user_profile=bundle.obj)
    #userlanguages = fields.ToManyField(UserLanguageResource, attribute=through_query, full=True)

    education = fields.ToManyField(UniversityResource, 'universities' , full=True)
    social_networks = fields.ToManyField(SocialNetworkResource, 'social_networks', full=True)
    instant_messages = fields.ToManyField(InstantMessageResource, 'instant_messages', full=True)
    current = fields.ToOneField(CityResource, 'current_city', full=True, null=True)
    hometown = fields.ToOneField(CityResource, 'hometown', full=True, null=True)
    other_locations = fields.ToManyField(CityResource, 'other_locations', full=True, null=True)
    interested_in = fields.ToManyField(InterestsResource, 'interested_in', full = True, null = True)

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
            'gender':['exact'],
            'languages':ALL_WITH_RELATIONS,
            #'userlanguages': ALL_WITH_RELATIONS,
        }
        excludes = ['pw_state', 'places_lived_in', 'places_visited', 'places_gonna_go', 'places_wanna_go']

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
        # capacity, start age, end age, language and type are OBLIGATORY        
        city = request.GET.get('wings', None)
        start_date = request.GET.get('startDate', None)
        end_date = request.GET.get('endDate', None)
        capacity = request.GET.get('capacity', None)
        start_age = request.GET.get('startAge', None)
        end_age = request.GET.get('endAge', None)
        language = request.GET.get('language', None)
        gender = request.GET.get('gender', None)
        tipo = request.GET.get('type', None)
        
        # QuerySets are lazy. This means that we can stack filters and there will be no database activity
        # until the queryset is evaluated.
        
        # filter by profile's parameters: start age, end age, language, gender
        if language and language != 'all':
            entry_query = self.get_query(language, ['userlanguage__language__name'])
            base_object_list = base_object_list.filter(entry_query).distinct()

        if start_age and end_age:
            base_object_list = base_object_list.filter(age__gte=int(start_age), age__lte=int(end_age)).distinct()

        if gender:
            entry_query = self.get_query(gender, ['gender'])
            base_object_list = base_object_list.filter(entry_query).distinct()

        # filter by wings' parameters: city, start date, end date, capacity, type
        if capacity or start_date or end_date or city or tipo:
            accomodation_list = Accomodation.objects.all()
            if capacity:
                accomodation_list = accomodation_list.filter(capacity__gte=capacity)
            if start_date:
                start_date = datetime.strptime(start_date, '%m-%d-%Y')
                accomodation_list = accomodation_list.exclude(date_end__isnull=False, date_end__lt=start_date)
            if end_date:
                end_date = datetime.strptime(end_date, '%m-%d-%Y')
                accomodation_list = accomodation_list.exclude(date_start__isnull=False, date_start__gt=end_date)
            if city:
                accomodation_list = accomodation_list.filter(city__name__iexact=city)
            if tipo:
                is_request = tipo == 'applicant'
                accomodation_list = accomodation_list.filter(is_request=is_request)
            base_object_list = base_object_list.filter(wing__in=accomodation_list).distinct()

        paginator = Paginator(base_object_list, 10)
        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        return page
        """
        base_object_list = super(UserProfileResource, self).apply_filters(request, applicable_filters)
        pprint(request.GET)
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
        """

    # funcion para trabajar con las wings de un profile. Por ejemplo, GET profiles/me/wings lista mis wings
    def prepend_urls(self):
        return [
            ##/profiles/<profile_id>|me/accomodations/
            url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/accomodations%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('accomodation_collection'), name="api_list_wings"), 
            ##/profiles/<profile_id>|me/accomodations/<accomodation_id> 
            url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/accomodations/(?P<wing_id>\w[\w/-]*)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('accomodation_detail'), name="api_detail_wing"),
            # /profiles/<profile_id>|me/relationships/
            url(r"^(?P<resource_name>%s)/(?P<profile_id>\w[\w/-]*)/relationships%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('relationship_collection'), name="api_list_relationships"),
            # /profiles/me/relationships/<profile_id>
            url(r"^(?P<resource_name>%s)/me/relationships/(?P<profile_id>\w[\w/-]*)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('relationship_detail'), name="api_detail_relationships"),
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

    
    #funcion llamada en el GET y que ha de devolver un objeto JSON con los idiomas hablados por el usuario
    def dehydrate_languages(self, bundle):
        for i in bundle.data['languages']: 
            # i.data = {id: id_language, name:'Spanish'}
            lang = i.obj
            ul = UserLanguage.objects.get(language=lang, user_profile=bundle.obj)
            i.data['level'] = str(ul.level).lower()
            i.data['name'] = str(i.data['name']).lower()
            #i.data.pop('id')
        return bundle.data['languages']

    def dehydrate_education(self, bundle):
        upu = UserProfileStudiedUniversity.objects.filter(user_profile=bundle.obj)
        res = []
        for u in upu:
            d = {}
            d['institution'] = u.university.name
            d['degree'] = u.degree
            res.append(d)
        return res
        """
        for i in bundle.data['education']: 
            # i.data = {id: id_university, name:'University of Reading'}
            uni = i.obj
            upu = UserProfileStudiedUniversity.objects.get(university=uni, user_profile=bundle.obj)
            i.data['degree'] = upu.degree
            i.data['institution'] = i.data['name']
            i.data.pop('id')
            i.data.pop('name')
        return bundle.data['education']
        """

    def dehydrate_social_networks(self, bundle):
        usn = UserSocialNetwork.objects.filter(user_profile=bundle.obj)
        res = []
        for u in usn:
            d = {}
            d['social_network'] = u.social_network.name
            d['sn_username'] = u.social_network_username
            res.append(d)
        return res
        """
        for i in bundle.data['social_networks']: 
            # i.data = {id: id_social_networks, name:'Facebook'}
            sn = i.obj
            usn = UserSocialNetwork.objects.get(social_network=sn, user_profile=bundle.obj)
            i.data['sn_username'] = usn.social_network_username
            i.data['social_network'] = i.data['name']
            i.data.pop('name')
            i.data.pop('id')
        return bundle.data['social_networks']
        """

    def dehydrate_instant_messages(self, bundle):
        uim = UserInstantMessage.objects.filter(user_profile=bundle.obj)
        res = []
        for u in uim:
            d = {}
            d['instant_message'] = u.instant_message.name
            d['im_username'] = u.instant_message_username
            res.append(d)
        return res
        """
        for i in bundle.data['instant_messages']: 
            # i.data = {id: id_instant_message, name:'Whatsapp'}
            im = i.obj
            uim = UserInstantMessage.objects.get(instant_message=im, user_profile=bundle.obj)
            i.data['im_username'] = uim.instant_message_username
            i.data['instant_message'] = i.data['name']
            i.data.pop('name')
            i.data.pop('id')
        return bundle.data['instant_messages']
        """
    
    def dehydrate_current(self, bundle):
        if bundle.data['current'] is None: return {} 
        city = bundle.data['current'].obj
        region = city.region
        country = region.country
        bundle.data['current'].data['region'] = region.name
        bundle.data['current'].data['country'] = country.name
        return bundle.data['current'].data

    def dehydrate_hometown(self, bundle):
        if bundle.data['hometown'] is None: return {} 
        city = bundle.data['hometown'].obj
        region = city.region
        country = region.country
        bundle.data['hometown'].data['region'] = region.name
        bundle.data['hometown'].data['country'] = country.name
        return bundle.data['hometown'].data

    def dehydrate_other_locations(self, bundle):
        for i in bundle.data['other_locations']: 
            # tenemos: i.data = {id, lat, lon, name}
            # queremos: i.data = {name, lat, lon, country, region}
            city = i.obj            
            region = city.region
            country = region.country
            i.data['region'] = region.name
            i.data['country'] = country.name
        return bundle.data['other_locations']

    """
    def dehydrate_birthday(self, bundle):
        bundle.data['birth_day'] = bundle.obj.birthday.day
        bundle.data['birth_month'] = bundle.obj.birthday.month
        bundle.data['birth_year'] = bundle.obj.birthday.year
        return bundle.data['birthday']
    """
    
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
        b = kwargs['pk'] == 'me'
        if b: kwargs['pk'] = UserProfile.objects.get(user=request.user).id
        a = super(UserProfileResource, self).get_detail(request, **kwargs)
        data = json.loads(a.content)
        data['pid'] = kwargs['pk']
        data['id'] = 'me'
        if b:
            up = UserProfile.objects.get(user=request.user)
            data['pw_state'] = up.pw_state
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
        self.is_valid(bundle, request)
        if bundle.errors:
            self.error_response(bundle.errors, request)

        up = UserProfile.objects.get(user=request.user)
        if 'interested_in' in bundle.data:
            up.interested_in = []
            for i in bundle.data['interested_in']:
                interest = Interests.objects.get(gender=i['gender'])
                up.interested_in.add(interest)
            bundle.data.pop('interested_in')

        if 'languages' in bundle.data:
            UserLanguage.objects.filter(user_profile_id=up.id).delete()
            for lang in bundle.data['languages']:
                try:
                    UserLanguage.objects.create(user_profile_id=up.id, language_id=Language.objects.get(name__iexact=lang['name']).id, level=lang['level'])
                except:
                    return self.create_response(request, {"msg":"Error: repeated languages.", "status":False, "code":413}, response_class=HttpForbidden)
            bundle.data.pop('languages')
        
        if 'education' in bundle.data:
            UserProfileStudiedUniversity.objects.filter(user_profile_id=up.id).delete()
            for e in bundle.data['education']:
                uni, b = University.objects.get_or_create(name=e['institution'])
                UserProfileStudiedUniversity.objects.create(user_profile_id=up.id, university_id=uni.id, degree=e['degree'])
            bundle.data.pop('education')

        if 'instant_messages' in bundle.data:
            UserInstantMessage.objects.filter(user_profile_id=up.id).delete()
            for im in bundle.data['instant_messages']:
                UserInstantMessage.objects.create(user_profile_id=up.id, instant_message_id=InstantMessage.objects.get(name=im['instant_message']).id, instant_message_username=im['im_username'])
            bundle.data.pop('instant_messages')

        if 'social_networks' in bundle.data:
            UserSocialNetwork.objects.filter(user_profile_id=up.id).delete()
            for sn in bundle.data['social_networks']:
                UserSocialNetwork.objects.create(user_profile_id=up.id, social_network_id=SocialNetwork.objects.get(name=sn['social_network']).id, social_network_username=sn['sn_username'])
            bundle.data.pop('social_networks')

        if 'current' in bundle.data:
            ccity = City.objects.saveLocation(**bundle.data['current'])
            up.current_city = ccity
            """
            if 'city' in bundle.data['current'] and 'region' in bundle.data['current'] and 'country' in bundle.data['current']:
                country, b = Country.objects.get_or_create(name=bundle.data['current']['country'])
                region, b = Region.objects.get_or_create(name=bundle.data['current']['region'], country=country)
                city, b = City.objects.get_or_create(name=bundle.data['current']['city'], region=region)
                up.current_city = city
            else:
                up.current_city = None
            """
            bundle.data.pop('current')

        if 'hometown' in bundle.data:
            hcity = City.objects.saveLocation(**bundle.data['hometown'])
            up.hometown = hcity
            """
            if 'city' in bundle.data['hometown'] and 'region' in bundle.data['hometown'] and 'country' in bundle.data['hometown']:
                country, b = Country.objects.get_or_create(name=bundle.data['hometown']['country'])
                region, b = Region.objects.get_or_create(name=bundle.data['hometown']['region'], country=country)
                city, b = City.objects.get_or_create(name=bundle.data['hometown']['city'], region=region)
                up.hometown = city
            else:
                up.hometown = None
            """
            bundle.data.pop('hometown')

        if 'other_locations' in bundle.data:
            up.other_locations = []
            for ol in bundle.data['other_locations']:
                ocity = City.objects.saveLocation(**ol)
                """
                country, b = Country.objects.get_or_create(name=ol['country'])
                region, b = Region.objects.get_or_create(name=ol['region'], country=country)
                city, b = City.objects.get_or_create(name=ol['city'], region=region)
                """
                if ocity is not None: up.other_locations.add(ocity)
            bundle.data.pop('other_locations')

        forbidden_fields_update = ['avatar', 'id', 'user']
        #not_empty_fields = ['pw_state', 'gender']

        if 'birth_day' in bundle.data: up.birthday = up.birthday.replace(day=int(bundle.data['birth_day']))
        if 'birth_month' in bundle.data: up.birthday = up.birthday.replace(month=int(bundle.data['birth_month']))
        if 'birth_year' in bundle.data: up.birthday = up.birthday.replace(year=int(bundle.data['birth_year']))
        if 'birthday' in bundle.data: del bundle.data['birthday']

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
        '''
        El get_list deberia devolver:
        - del modelo User: first_name, last_name, last_login
        - de UserProfile: avatar, age, languages + levels, occupation, all_about_you, uri, current_city

        + correcciones: elegir entre last_login y online, si online => localizacion actual en vez de current_city
        + futuro: resto de fotos, num_friends, num_references, verificado, tasa de respuestas, pending/accepted... de la misma ala que busco
        '''
        objects = {'count':len(data), 'profiles':data}
        content = {}  
        content['msg'] = 'Profiles retrieved successfully.'      
        content['status'] = True
        content['code'] = 200
        content['data'] = objects
        return self.create_response(request, content, response_class=HttpResponse)

    def full_dehydrate(self, bundle):
        bundle = super(UserProfileResource, self).full_dehydrate(bundle)

        if bundle.request.path not in (self.get_resource_uri(bundle), u'/api/v1/profiles/me'):
            # venimos de get_list => solamente devolver los campos requeridos
            permitted_fields = ['avatar', 'age', 'languages', 'occupation', 'all_about_you', 'current', 'user', 'verified', 'num_friends', 'num_references', 'pending', 'tasa_respuestas']
            '''
            De user:
            
            bundle.data['last_login'] = bundle.obj.user.last_login
            De user profile:
            bundle.data['avatar'] = bundle.obj.avatar
            bundle.data['age'] = bundle.obj.age
            bundle.data['languages'] = bundle.obj.languages
            bundle.data['languages'] = self.dehydrate_languages(bundle)
            bundle.data['occupation'] = bundle.obj.occupation
            bundle.data['all_about_you'] = bundle.obj.all_about_you
            bundle.data['current_city'] = bundle.obj.current_city
            #bundle.data['user'] = bundle.obj.current_city
            '''
            for key, value in bundle.data.items():
                if key not in permitted_fields: del bundle.data[key]
            bundle.data['first_name'] = bundle.obj.user.first_name
            bundle.data['last_name'] = bundle.obj.user.last_name
            bundle.data['verified'] = True
            bundle.data['num_friends'] = 0
            bundle.data['num_references'] = 0
            bundle.data['pending'] = "Pending"
            bundle.data['tasa_respuestas'] = 0

            from datetime import timedelta
            d = timedelta(hours=1)
            online = ApiToken.objects.filter(user=bundle.obj.user, last__gte=date.today()-d).exists()
            if online: bundle.data['last_login'] = "Online"
            else: bundle.data['last_login'] = bundle.obj.user.last_login.strftime("%a %b %d %H:%M:%S %Y")
            #print bundle.obj.user.last_login
            #print datetime.now().timetz()

            if 'lat' in bundle.data['current']: del bundle.data['current']['lat']
            if 'lon' in bundle.data['current']: del bundle.data['current']['lon']            

            if bundle.request.user.is_anonymous():
                # borroneo
                from django.conf import settings as django_settings
                bundle.data['avatar'] = '%sblank_avatar.jpg' % django_settings.MEDIA_URL

                long_first = len(bundle.obj.user.first_name)
                long_last = len(bundle.obj.user.last_name)
                import string, random
                ran_name = [random.choice(string.ascii_letters) for n in xrange(long_first)]
                ran_last = [random.choice(string.ascii_letters) for n in xrange(long_last)]
                ran_name = "".join(ran_name)
                ran_last = "".join(ran_last)
                bundle.data['first_name'] = ran_name
                bundle.data['last_name'] = ran_last
        else:  
            # venimos de get_detail y ademas el usuario esta logueado
            if bundle.request.path != u'/api/v1/profiles/me':
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
                errors = {}
                content['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                content = {}
                errors = {}
                content['msg'] = "Error in some fields validation"
                content['code'] = 410
                content['status'] = False
                content['errors'] = json.loads(e.messages)
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                # This exception occurs when the JSON is not a JSON...
                content = {}
                errors = {}
                content['code'] = 411
                content['status'] = False
                content['msg'] = e
                return self.create_response(request, content, response_class = HttpResponse)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpMethodNotAllowed)):
                    content = {}
                    errors = {}
                    content['msg'] = "Method not allowed"                               
                    content['code'] = 412
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpUnauthorized)):
                    content = {}
                    errors = {}
                    content['msg'] = "Unauthorized"                               
                    content['code'] = 413
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                elif (isinstance(e.response, HttpApplicationError)):
                    content = {}
                    errors = {}
                    content['msg'] = "Can't logout"                               
                    content['code'] = 400
                    content['status'] = False
                    return self.create_response(request, content, response_class = HttpResponse)
                else:               
                    content = {}
                    errors = {}
                    content['msg'] = "Error in some fields."               
                    content['code'] = 400
                    content['status'] = False
                    if 'profiles' in e.response.content: errors = json.loads(e.response.content)['profiles']
                    else: errors = json.loads(e.response.content)['accomodations']
                    content['errors'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
            except Exception, e:
                return self._handle_500(request, e)

        return wrapper


