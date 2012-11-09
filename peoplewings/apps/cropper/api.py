
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import NotRegistered, BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError
from django.http import HttpResponse

from peoplewings.apps.cropper.models import Cropped, Original
from peoplewings.apps.cropper.form import CropperForm
from peoplewings.apps.registration.authentication import ApiTokenAuthentication
from peoplewings.apps.people.models import UserProfile

from tastypie.utils import dict_strip_unicode_keys

class CropperResource(Resource):
    
    
    class Meta:
        object_class = Cropper
        queryset = Cropper.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=CropperForm)
  
    def post_detail(self, request, **kwargs):
        #kwargs = id de la original
        #raw_post_data = x, y, w, h   
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
     
        cropped_img = Cropper()
        try:
            cropped_img.original = Original.objects.get(pk=kwargs['id'])
            cropped_img.x = bundle.data['x']
            cropped_img.y = bundle.data['y']
            cropped_img.w = bundle.data['w']
            cropped_img.h = bundle.data['h']
            cropped_img.save()
            up = UserProfile.objects.get(pk = cropped_img.original.owner_id)
            up.avatar = cropped_img.image.url
            up.save()
            return self.create_response(request, {"status":True, "data":"Avatar cropped and updated", "code":"200"}, response_class = HttpResponse)
        except Exception, e:
            return self.create_response(request, {"status":False, "data":"The original image or user does not exists", "code":"403"}, response_class = HttpResponse)
        

    def wrap_view(self, view):

        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                varies = getattr(self._meta.cache, "varies", [])

                if varies:
                    patch_vary_headers(response, varies)

                if self._meta.cache.cacheable(request, response):
                    if self._meta.cache.cache_control():
                        patch_cache_control(response, **self._meta.cache.cache_control())

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
    
