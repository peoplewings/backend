
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
<<<<<<< HEAD
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpAccepted

from django.utils.cache import *
from django import http as djangoHttp
from django.views.decorators.csrf import csrf_exempt
from django.forms import ValidationError

from peoplewings.apps.wings.models import Wing
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
=======
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpResponse
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource
from peoplewings.apps.wings.models import Wing
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer


>>>>>>> 1

class WingsResource(ModelResource):
    
    class Meta:
        object_class = Wing
        queryset = Wing.objects.all()
        allowed_methods = ['patch']
        include_resource_uri = False
        resource_name = 'wings'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=UserSignUpForm)

    def prepend_urls(self):      
        return [
            url(r"^(?P<resource_name>%s)/me%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/(?P<wing_id>[\d]+)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def post_detail(self, request, **kwargs):
        ##TODO
        print 'hola'
        return self.create_response(request, bundle, response_class = HttpResponse)
    
    def patch_detail(self, request, **kwargs):
        print 'PATCH DETAIL'        
        return self.create_response(request, {}, response_class=HttpAccepted)

    def post_detail(self, request, **kwargs):
        if 'HTTP_X_HTTP_METHOD_OVERRIDE' in request.META:
            print 'PUTA MIERDA'
        print 'POST DETAIL'        
        return self.create_response(request, {}, response_class=HttpAccepted)

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
    
