
from django.conf.urls.defaults import url
from django.views.decorators.csrf import csrf_exempt
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.cache import *
from django import http as djangoHttp
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from tastypie import fields
from tastypie import *
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse, NotFound
from tastypie.http import HttpBadRequest, HttpApplicationError, HttpAccepted, HttpResponse, HttpForbidden
from tastypie.utils import trailing_slash, dict_strip_unicode_keys
from tastypie.resources import ModelResource

from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.wings.models import Accomodation
from peoplewings.apps.wings.forms import *
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.locations.models import City, Region, Country
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.wings.exceptions import BadParameters, NotAUser

from pprint import pprint

class AccomodationsResource(ModelResource):
    
    class Meta:
        object_class = Accomodation
        queryset = Accomodation.objects.all()
        allowed_methods = ['get', 'post', 'delete']
        include_resource_uri = False
        resource_name = 'accomodations'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=AccomodationForm)

    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('POST', 'DELETE'):
            up = UserProfile.objects.get(user=request.user)
            return object_list.filter(author=up)
        return object_list 
    

    def obj_create(self, bundle, request=None, **kwargs):
        if kwargs['profile_id'] != 'me':
            bundle.errors = {"code": 401, "status": False, "errors":"The wing provided does not exist or does not belong to the user given"}
            return bundle
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        setattr(bundle.obj, 'author', UserProfile.objects.get(user=request.user))
        
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

    @transaction.commit_on_success
    def delete_detail(self, request, **kwargs):
        if kwargs['profile_id'] != 'me':
            return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpForbidden)
        try:
            up = UserProfile.objects.get(user=request.user)
            a = Accomodation.objects.get(author_id=up.id, pk=kwargs['wing_id'])
            a.delete()
            bundle = self.build_bundle(data={"code": 200, "status": True, "message":"Wing deleted"}, request=request)
            return self.create_response(request, bundle, response_class = HttpResponse)
        except NotFound:
            return http.HttpNotFound()
        except ObjectDoesNotExist:
            bundle = {"code": 401, "status": False, "errors":"The wing provided does not exist or does not belong to the user given"}
            return self.create_response(request, bundle, response_class = HttpResponse)

    def delete_list(self, request=None, **kwargs):
        return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpResponse)

    def get_list(self, request, **kwargs):       
        try:
            if 'author_id' in kwargs:
                if kwargs['author_id'] == 'me': kwargs['author_id'] = UserProfile.objects.get(user=request.user)
                else: kwargs['author_id'] = UserProfile.objects.get(pk=kwargs['author_id'])
        except:
            return self.create_response(request, {"code" : 401, "status" : False, "errors": "Not found"}, response_class=HttpResponse)
        return super(AccomodationsResource, self).get_list(request, **kwargs)

    def get_detail(self, request, **kwargs):
        if 'author_id' not in kwargs: return self.create_response(request, {"code" : 401, "status" : False, "errors": "Not implemented"}, response_class=HttpResponse)
        try:            
            if kwargs['author_id'] == 'me': kwargs['author_id'] = UserProfile.objects.get(user=request.user)
            else: kwargs['author_id'] = UserProfile.objects.get(pk=kwargs['author_id'])
        except:
            return self.create_response(request, {"code" : 401, "status" : False, "errors": "Not found"}, response_class=HttpResponse)
         
        return super(AccomodationsResource, self).get_detail(request, **kwargs)

    @transaction.commit_on_success
    def post_detail(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        self.is_valid(bundle, request)
        try:
            a = Accomodation.objects.get(pk=kwargs['wing_id'])
        except ObjectDoesNotExist:
            bundle = {"code": 401, "status": False, "errors":"The wing provided does not exist"}
            return self.create_response(request, bundle, response_class = HttpResponse)

        wing_author = a.author
        connected_profile = UserProfile.objects.get(user=request.user)
        if kwargs['profile_id'] == 'me': kwargs['profile_id'] = connected_profile.id
        provided_author_id = int(kwargs['profile_id'])

        if wing_author.id != provided_author_id:
            bundle = {"code": 401, "status": False, "errors":"The user given and the user connected don't match"}
            return self.create_response(request, bundle, response_class = HttpResponse)

        loc = {}
        data = bundle.data['city']
        for key, value in data.items():            
            loc[key] = value
        city = City.objects.saveLocation(**loc)
        setattr(a, 'city', city)
        bundle.data.pop('city')

        if wing_author.id == connected_profile.id:
            for i in bundle.data:
                if hasattr(a, i): 
                    if i == 'author_id':
                        bundle = {"code": 401, "status": False, "errors":"The wing ownership cannot change"}
                        return self.create_response(request, bundle, response_class = HttpResponse)
                    setattr(a, i, bundle.data.get(i))
        else:
            bundle = {"code": 401, "status": False, "errors":"The wing provided does not belong to the user connected"}
            return self.create_response(request, bundle, response_class = HttpResponse)
        
        #updated_bundle = self.dehydrate(bundle)
        #updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        a.save()
        self.save_related(bundle)
        bundle = {"code" : 200, "status" : True, "data" : "OK"}
        return self.create_response(request, bundle, response_class=HttpAccepted) 

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
            except (BadRequest, fields.ApiFieldError, NotAUser), e:
                return http.HttpBadRequest(e.args[0])
            except ValidationError, e:
                return http.HttpBadRequest(', '.join(e.messages))
            except Exception, e:
                if hasattr(e, 'response'):
                    return e.response
                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise
                return self._handle_500(request, e)

        return wrapper
    
