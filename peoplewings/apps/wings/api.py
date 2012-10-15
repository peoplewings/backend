
from django.conf.urls.defaults import url
from django.views.decorators.csrf import csrf_exempt
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.cache import *
from django import http as djangoHttp
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.models import AnonymousUser

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
from peoplewings.apps.wings.exceptions import BadParameters, NotAUser

from pprint import pprint

class AccomodationsResource(ModelResource):
    is_anonymous = False
    city = fields.ToOneField(CityResource, 'city', full=True, null=True)

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
        print "--- in apply_authorization_limits ---"
        print "request: (encontrar aqui si el metodo es list o detail) "
        pprint(request)
        if request.method not in ('GET'):
            up = UserProfile.objects.get(user=request.user)
            return object_list.filter(author=up)
        return object_list

    """
    def dehydrate(self, bundle):
        if hasattr(bundle, 'errors'):
            bundle.data = {}
            bundle.data['status'] = bundle.errors['code']
            bundle.data['code'] = bundle.errors['status']
            bundle.data['data'] = bundle.errors['errors']
            return bundle
        if self.is_anonymous: 
            print "Anonymous!!"
            pprint(bundle.data)
        return super(AccomodationsResource, self).dehydrate(bundle)
    """


    def obj_create(self, bundle, request=None, **kwargs):
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpForbidden)

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

    def get_list(self, request, **kwargs):
        print "hola"
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpForbidden)
        
        up = UserProfile.objects.get(user=request.user)        
        if kwargs['profile_id'] == 'me': kwargs['profile_id'] = up.id
        accomodations = Accomodation.objects.filter(author_id=kwargs['profile_id'])
        objects = []
        for i in accomodations:
            bundle = self.build_bundle(obj=i, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        return self.create_response(request, objects)
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
    """
    def post_list(self, request, **kwargs):
        return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpForbidden)
    """
    def delete_list(self, request=None, **kwargs):
        return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpForbidden)

    def get_detail(self, request, **kwargs):
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpForbidden)

        up = UserProfile.objects.get(user=request.user)
        if kwargs['profile_id'] == 'me': kwargs['profile_id'] = up.id
        try:
            a = Accomodation.objects.get(author_id=kwargs['profile_id'], pk=kwargs['wing_id'])
            bundle = self.build_bundle(obj=a, request=request)
            bundle = self.full_dehydrate(bundle)
        except ObjectDoesNotExist:
            bundle = {"code": 401, "status": False, "errors":"The wing provided does not exist or does not belong to the user given"}
            return self.create_response(request, bundle, response_class = HttpResponse)
        return self.create_response(request, bundle)


    @transaction.commit_on_success
    def post_detail(self, request, **kwargs):
        if 'profile_id' not in kwargs:
            return self.create_response(request, {"code" : 401, "status" : False, "errors": "Unauthorized"}, response_class=HttpForbidden)

        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        self.is_valid(bundle, request)
        try:
            a = Accomodation.objects.get(pk=kwargs['wing_id'], author=UserProfile.objects.get(user=request.user))
        except ObjectDoesNotExist:
            bundle = {"code": 401, "status": False, "errors":"The wing provided does not exist or does not belong to you!"}
            return self.create_response(request, bundle, response_class = HttpResponse)

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
            if hasattr(a, i): setattr(a, i, bundle.data.get(i))
        
        #updated_bundle = self.dehydrate(bundle)
        #updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        a.save()
        self.save_related(bundle)
        bundle = {"code" : 200, "status" : True, "data" : "Wing updated ;-)"}
        return self.create_response(request, bundle, response_class=HttpAccepted)

    @transaction.commit_on_success
    def delete_detail(self, request, **kwargs):
        if 'profile_id' not in kwargs:
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
    
