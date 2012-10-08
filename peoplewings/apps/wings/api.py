
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
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource

from django.utils.cache import *
from django import http as djangoHttp
from django.views.decorators.csrf import csrf_exempt
from django.forms import ValidationError

from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.wings.models import Accomodation
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer

class AccomodationResource(ModelResource):
    
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

    def get_list(self, request, **kwargs):
        print "holaaaa"
        import pprint

        print request.user.email
        kwargs['pk'] = UserProfile.objects.get(user=request.user).id
        return super(AccomodationResource, self).get_list(request, **kwargs)

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
    
