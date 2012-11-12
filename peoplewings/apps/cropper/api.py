
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpMethodNotAllowed
from tastypie.utils import trailing_slash
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.utils.cache import patch_cache_control
from django.contrib.auth.models import User
from django.conf.urls import url
from django.contrib.auth import authenticate
from django.http import HttpResponse

from peoplewings.apps.cropper.models import Cropped, Original
from peoplewings.apps.cropper.forms import CroppedForm
from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.people.models import UserProfile

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from tastypie.utils import dict_strip_unicode_keys

class CroppedResource(ModelResource):
    
    
    class Meta:
        object_class = Cropped
        queryset = Cropped.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=CroppedForm)
  
    def post_detail(self, request, **kwargs):
        #kwargs = id de la original
        #raw_post_data = x, y, w, h   
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
     
        cropped_img = Cropped()
        try:
            cropped_img.original = Original.objects.get(pk=kwargs['pk'])            
            cropped_img.x = int(bundle.data['x'])
            cropped_img.y = int(bundle.data['y'])
            cropped_img.w = int(bundle.data['w'])
            cropped_img.h = int(bundle.data['h'])
            cropped_img.cropit()
            if cropped_img is not None:
                cropped_img.save()
                up = UserProfile.objects.get(user = request.user.pk)
                up.avatar = cropped_img.image.url

                up.save()
            else:
                return self.create_response(request, {"status":False, "data":"The image could not be cropped", "code":"403"}, response_class = HttpResponse)
            return self.create_response(request, {"status":True, "data":"Avatar cropped and updated", "code":"200"}, response_class = HttpResponse)
        except Exception, e: 
            print e           
            return self.create_response(request, {"status":False, "data":"The original image or user does not exists", "code":"403"}, response_class = HttpResponse)
        

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)              

                return response
            except (BadRequest, fields.ApiFieldError), e:
                return http.HttpBadRequest(e.args[0])
            except ValidationError, e:
                return http.HttpBadRequest(', '.join(e.messages))
            except Exception, e:
                if hasattr(e, 'response'):
                    return e.response

                # A real, non-expected exception.
                # Handle the case where the full traceback is more helpful
                # than the serialized error.
                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise

                # Re-raise the error to get a proper traceback when the error
                # happend during a test case
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise

                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper
    
