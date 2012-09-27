#Registration API
from django.contrib.auth.models import User
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

from peoplewings.apps.registration.models import RegistrationProfile
from peoplewings.apps.registration.views import register    
from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.apps.registration.views import UserSignUpForm

class UserSignUpResource(ModelResource):
    
    form_data = None
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'newuser'
        #excludes = ['is_active', 'is_staff', 'is_superuser']
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserSignUpForm)

    def obj_create(self, bundle, request=None, **kwargs):
        request.POST = bundle.data
        self.form_data = register(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')            
        return bundle

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id, is_superuser=True)

    def dehydrate(self, bundle):
        bundle.data = {}
        if self.form_data and self.form_data._errors:
            bundle.data['status'] = False
            bundle.data['code'] = 401
            bundle.data['errors'] = self.form_data._errors
        else:
            bundle.data['status'] = True
            bundle.data['code'] = 201
            bundle.data['data'] = 'Registration complete'        
        return bundle

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                # response is a HttpResponse object, so follow Django's instructions
                # to change it to your needs before you return it.
                # https://docs.djangoproject.com/en/dev/ref/request-response/
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
                bundle = {"code": 777, "status": False, "error": json.loads(e.response.content)}
                return self.create_response(request, bundle, response_class = HttpBadRequest)          
            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper

class UserResource(ModelResource):
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'user/activation'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=ActivationForm)

        def obj_create(self, bundle, request=None, **kwargs):
            request.POST = bundle.data
            self.form_data = register(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')            
            return bundle



