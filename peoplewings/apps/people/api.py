#People API
from peoplewings.apps.people.models import UserProfile
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
from django.db import IntegrityError
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

class UserProfileResource(ModelResource):    
    user = fields.ToOneField(AccountResource, 'user')
    method = None
    class Meta:
        object_class = UserProfile
        queryset = UserProfile.objects.all()
        allowed_methods = ['get', 'post']
        include_resource_uri = False
        resource_name = 'profile'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserProfileForm)

    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('GET'):  # 1.
            return object_list.filter(user=request.user)

    def post_detail(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)       
        up = UserProfile.objects.get(user=request.user)
        for i in bundle.data:
            setattr(up, i, bundle.data.get(i))
        up.save()
        self.method = 'POST'
        updated_bundle = self.dehydrate(bundle)
        updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        return self.create_response(request, updated_bundle, response_class=HttpAccepted) 
    
    def post_list(self, request, **kwargs):
        return self.create_response(request, {}, response_class=HttpForbidden)

    def dehydrate(self, bundle):
        print 'METHOD: ', self.method
        if self.method:
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 204
            bundle.data['data'] = 'Updated'
            return bundle   
        else:
             return super(UserProfileResource, self).dehydrate(bundle)        
    
    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):    
            try:
                callback = getattr(self, view)
                #pprint.pprint(request.META['HTTP_ID'])
                response = callback(request, *args, **kwargs)
                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                return response
            except BadRequest, e:
                return HttpBadRequest({'code': 666, 'message':e.args[0]})
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                bundle = {"code": 777, "status": False, "error": json.loads(e.messages)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)
            except ImmediateHttpResponse, e:
                if (isinstance(e.response, HttpUnauthorized)):
                    bundle = {"code": 401, "status": False, "error":"Unauthorized"}
                    return self.create_response(request, bundle, response_class = HttpUnauthorized)
                if (isinstance(e.response, HttpApplicationError)):
                    bundle = {"code": 401, "status": False, "error":"Error"}
                    return self.create_response(request, bundle, response_class = HttpApplicationError)          
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper

    
