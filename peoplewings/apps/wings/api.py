
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
from peoplewings.apps.wings.models import Accomodation
from peoplewings.apps.wings.forms import *
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.locations.models import City, Region, Country
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.locations.api import CityResource

from pprint import pprint

import json

class AccomodationsResource(ModelResource):
    #is_anonymous = False
    city = fields.ToOneField(CityResource, 'city', full=True, null=True)

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
            return self.create_response(request, {"msg":"Error: missing profile id." ,"code" : 413, "status" : False}, response_class=HttpForbidden)
        
        self.is_valid(bundle, request)
        if bundle.errors:
            self.error_response(bundle.errors, request)


        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
 
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
        for key, value in bundle.data.items():
            if hasattr(a, key): setattr(a, key, value)

        a.save()

        bundle = self.build_bundle(obj=a, request=request)
        return bundle

        """
        up = UserProfile.objects.get(user=request.user)
        kwargs['author_id'] = up.id
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            if hasattr(bundle.obj, key): setattr(bundle.obj, key, value)

        setattr(bundle.obj, 'author', up)
        
        loc = {}
        data = bundle.data['city']
        for key, value in data.items():            
            loc[key] = value

        city = City.objects.saveLocation(**loc)
        setattr(bundle.obj, 'city', city)
        bundle = self.full_hydrate(bundle)
        self.is_valid(bundle,request)

        if hasattr(bundle, 'errors') and bundle.errors:
            self.error_response(bundle.errors, request)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save parent
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle
        """

    def get_list(self, request, **kwargs):
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"msg":"Error: the uri is not correct: missing profile id.", "code" : 413, "status" : False}, response_class=HttpForbidden)
        
        up = UserProfile.objects.get(user=request.user)        
        if kwargs['profile_id'] == 'me': kwargs['profile_id'] = up.id

        try:
            accomodations = Accomodation.objects.filter(author_id=kwargs['profile_id'])
        except:
            return self.create_response(request, {"msg":"Error: User not found.", "code" : 413, "status" : False}, response_class=HttpForbidden)
        
        objects = []
        for i in accomodations:
            bundle = self.build_bundle(obj=i, request=request)
            bundle = self.full_dehydrate(bundle)
            dic = {}
            dic['name'] = bundle.data['name']
            dic['uri'] = str.replace(bundle.data['resource_uri'], 'me', str(up.id))
            bundle.data = dic
            objects.append(bundle)

        return self.create_response(request, {"msg":"Accommodations retrieved successfully.", "code":200, "status":True, "data":objects})
        """
        self.is_anonymous = request.user.is_anonymous()


        if not self.is_anonymous:
            up = UserProfile.objects.get(user=request.user)        
            if kwargs['profile_id'] == 'me': kwargs['profile_id'] = up.id
            accomodations = Accomodation.objects.filter(author_id=kwargs['profile_id'])
        else: 
            accomodations = Accomodation.objects.all()
        objects = []
        for i in accomodations:
            bundle = self.build_bundle(obj=i, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        return self.create_response(request, objects)
        """
    
    def post_list(self, request, **kwargs):
        up = UserProfile.objects.get(user=request.user)
        if 'profile_id' not in kwargs or kwargs['profile_id'] not in ('me', str(up.id)):
            return self.create_response(request, {"code" : 401, "status" : False, "msg": "Unauthorized"}, response_class=HttpForbidden)
        a = super(AccomodationsResource, self).post_list(request, **kwargs)
        data = {}
        data['uri'] = json.loads(a.content)['resourceUri']
        dic = {"msg":"Accommodation created successfully.", "data":data, "status":True, "code":200}
        return self.create_response(request, dic)

    def get_detail(self, request, **kwargs):
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"msg":"Error: the uri provided is not correct: missing profile id", "code" : 413, "status" : False}, response_class=HttpForbidden)

        up = UserProfile.objects.get(user=request.user)
        if kwargs['profile_id'] == 'me': kwargs['profile_id'] = up.id
        try:
            a = Accomodation.objects.get(author_id=kwargs['profile_id'], pk=kwargs['wing_id'])
        except:
            return self.create_response(request, {"msg":"Error: Wing not found for that user.", "code" : 413, "status" : False}, response_class=HttpForbidden)
        bundle = self.build_bundle(obj=a, request=request)
        bundle = self.full_dehydrate(bundle)
        return self.create_response(request, {"msg":"Accommodation retrieved successfully.", "code":200, "status":True, "data":bundle})

    def patch_detail(self, request, **kwargs):
        return self.put_detail(request, **kwargs)    

    @transaction.commit_on_success
    def put_detail(self, request, **kwargs):
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"msg":"Error: the uri provided is not correct: profile id missing.", "code" : 413, "status" : False}, response_class=HttpForbidden)

        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)

        self.is_valid(bundle, request)
        if bundle.errors:
            self.error_response(bundle.errors, request)
        try:
            a = Accomodation.objects.get(pk=int(kwargs['wing_id']), author=UserProfile.objects.get(user=request.user))
        except:
            return self.create_response(request, {"msg":"Error: Wing not found for that user.", "code" : 413, "status" : False}, response_class=HttpForbidden)
        if 'city' in bundle.data:
            loc = {}
            data = bundle.data['city']
            for key, value in data.items():            
                loc[key] = value
            city = City.objects.saveLocation(**loc)
            setattr(a, 'city', city)
            bundle.data.pop('city')

        if 'author_id' in bundle.data: bundle.data.pop('author_id')
        for i in bundle.data:
            if hasattr(a, i):
                """               
                if i == 'dateStart' or i == 'dateEnd':
                    aux = datetime.strptime(bundle.data.get(i), '%Y-%m-%d')
                    setattr(a, i, aux)
                else: setattr(a, i, bundle.data.get(i))
                """
                setattr(a, i, bundle.data.get(i))
        
        #updated_bundle = self.dehydrate(bundle)
        #updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        a.save()
        self.save_related(bundle)
        bundle = {"code" : 200, "status" : True, "msg" : "Accommodation updated successfully."}
        return self.create_response(request, bundle, response_class=HttpAccepted)

    @transaction.commit_on_success
    def delete_detail(self, request, **kwargs):
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"msg":"Error: uri incorrect: profile id is missing." , "code" : 413, "status" : False}, response_class=HttpForbidden)
        up = UserProfile.objects.get(user=request.user)
        try:
            a = Accomodation.objects.get(author_id=up.id, pk=kwargs['wing_id'])
        except:
            return self.create_response(request, {"msg":"Error: Wing not found for that user.", "code" : 413, "status" : False}, response_class=HttpForbidden)
        a.delete()
        bundle = self.build_bundle(data={"code": 200, "status": True, "msg":"Accommodation deleted successfully."}, request=request)
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
        return super(AccomodationsResource, self).full_dehydrate(bundle)
    
    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                varies = getattr(self._meta.cache, "varies", [])

                if varies:
                    patch_vary_headers(response, varies)             

                if request.is_ajax() and not response.has_header("Cache-Control"):
                    patch_cache_control(response, no_cache=True)

                return response
            except BadRequest, e:
                content = {}
                errors = {}
                content['msg'] = e.args[0]               
                content['code'] = 400
                content['status'] = False
                return self.create_response(request, content, response_class = HttpResponse) 
            except ValidationError, e:
                content = {}
                errors = {}
                content['msg'] = "Error in some fields"
                content['code'] = 410
                content['status'] = False
                content['errors'] = json.loads(e.messages)
                return self.create_response(request, content, response_class = HttpResponse)
            except ValueError, e:
                content = {}
                errors = {}
                content['msg'] = "No JSON could be decoded"               
                content['code'] = 411
                content['status'] = False
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
                    errors = json.loads(e.response.content)['accomodations']
                    content['errors'] = errors
                    return self.create_response(request, content, response_class = HttpResponse)
            except Exception, e:
                return self._handle_500(request, e)

        return wrapper
    
