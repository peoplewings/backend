
from django.conf.urls.defaults import url
from django.views.decorators.csrf import csrf_exempt
from django.forms import ValidationError

from tastypie import fields
from tastypie import *
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpAccepted, HttpResponse
from tastypie.utils import trailing_slash, dict_strip_unicode_keys
from tastypie.resources import ModelResource
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

from django.utils.cache import *
from django import http as djangoHttp
from django.views.decorators.csrf import csrf_exempt
from django.forms import ValidationError


from peoplewings.apps.wings.models import Accomodation
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.locations.models import City, Region, Country
from peoplewings.apps.people.models import UserProfile

from pprint import pprint

class AccomodationsResource(ModelResource):
    
    class Meta:
        object_class = Accomodation
        queryset = Accomodation.objects.all()
        allowed_methods = ['get', 'post', 'put', 'delete']
        include_resource_uri = False
        resource_name = 'accomodations'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=UserSignUpForm)

    def obj_create(self, bundle, request=None, **kwargs):

        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        setattr(bundle.obj, 'author', UserProfile.objects.get(user=request.user))
        
        loc = {}
        data = bundle.data['city']
        for key, value in data.items():            
            loc[key] = value
        print loc
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

    def post_detail(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)

        a = Accomodation.objects.get(wing_ptr=kwargs['wing_id'])
        up = a.author
        up2 = UserProfile.objects.get(user=request.user)
        if up.id == up2.id:
            pprint(bundle.data)
            for i in bundle.data:
                if hasattr(a, i): setattr(a, i, bundle.data.get(i))
            a.save()


        updated_bundle = self.dehydrate(bundle)
        updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        return self.create_response(request, updated_bundle, response_class=HttpAccepted) 

    def get_detail(self, request, **kwargs):
        print kwargs
        pprint(request)
        return super(AccomodationsResource, self).get_detail(request, **kwargs)

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
            except (BadRequest, fields.ApiFieldError), e:
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
    
