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
from tastypie.http import HttpBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError
from django.forms import ValidationError
from django.utils.cache import patch_cache_control

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer

from django.core import serializers
import json
from django.http import HttpResponse
from peoplewings.apps.registration.api import UserResource
from peoplewings.apps.people.forms import UserProfileForm

class UserProfileResource(ModelResource):
    
    form_data = None
    class Meta:
        object_class = UserProfile
        queryset = UserProfile.objects.all()
        allowed_methods = ['get', 'post']
        include_resource_uri = False
        resource_name = 'profile'
        #excludes = ['is_active', 'is_staff', 'is_superuser']
        #fields = ['pw_state', 'avatar']
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserProfileForm)


    def get_detail(self, request, **kwargs):
        up = UserProfile.objects.get(pk=kwargs['pk'])
        response = serializers.serialize("json", UserProfile.objects.all().filter(pk=kwargs['pk']), indent=2)
        return HttpResponse(response)

    def post_detail(self, request, **kwargs):
        #print kwargs
        import pprint
        pprint.pprint(request.POST)
        #print "received age: ", request.POST.__getitem__("age")
        up = UserProfile.objects.get(pk=kwargs['pk'])
        for i in request.POST: print i
        f = UserProfileForm(request.POST)


    def post_list(self, request, **kwargs):
        print "/// Entrada a post_list ///"

    def get_list(self, request, **kwargs):
        #print "//// Entrada a get_list ////"
        response = serializers.serialize("json", UserProfile.objects.all(), indent=2)
        return HttpResponse(response)

    def obj_create(self, bundle, **kwargs):
        print "/// Entrada a obj_create ///"

    def obj_update(self, bundle, **kwargs):
        print "/// Entrada a obj_update ///" 

    """
    def full_dehydrate(self, bundle):
        print "entramos en dehydrate"
        print bundle
        bundle.data = {}
        if self.form_data and self.form_data._errors:
            bundle.data['status'] = False
            bundle.data['code'] = 401
            bundle.data['errors'] = self.form_data._errors
        else:
            bundle.data['status'] = True
            bundle.data['code'] = 201
            bundle.data['data'] = 'Profile Complete ;-)'        
        return bundle
    """

    def dehydrate(self, bundle):
        print "entramos en dehydrate"
        bundle.data['status'] = True
        bundle.data['code'] = 201       
        return bundle

    def full_dehydrate(self, bundle):
        print "entramos en dehydrate"
        token = bundle.data
        bundle.data = {}
        bundle.data['status'] = True
        bundle.data['code'] = 201 
        bundle.data['token'] = token      
        return bundle


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
                bundle = {"code": 777, "status": False, "error": e}
                return self.create_response(request, bundle, response_class = HttpBadRequest)          
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper

    