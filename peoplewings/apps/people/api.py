#People API
from peoplewings.apps.people.models import UserProfile, UserLanguage, Language
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
from django.db import IntegrityError, transaction
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
from peoplewings.global_vars import LANGUAGES_LEVEL_CHOICES_KEYS



class LanguageResource(ModelResource):
    #languages = fields.ToManyField('peoplewings.apps.people.api.UserLanguageResource', 'languages')
    class Meta:
        object_class = Language
        queryset = Language.objects.all()
        allowed_methods = []
        include_resource_uri = False
        #resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=UserProfileForm)


class UserLanguageResource(ModelResource):    
    language = fields.ToOneField(LanguageResource, 'language', full=True)
    user_profile = fields.ToOneField('apps.people.api.UserProfileResource', 'user_profile')

    class Meta:
        object_class = UserLanguage
        queryset = UserLanguage.objects.all()
        allowed_methods = []
        include_resource_uri = False
        #resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        #validation = FormValidation(form_class=UserProfileForm)

class UserProfileResource(ModelResource):    
    user = fields.ToOneField(AccountResource, 'user')
    languages = fields.ToManyField(LanguageResource, 'languages', full=True)
    #education = fields.ToManyField()
    method = None
    class Meta:
        object_class = UserProfile
        queryset = UserProfile.objects.all()
        allowed_methods = ['get', 'post']
        include_resource_uri = False
        resource_name = 'profiles'
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        validation = FormValidation(form_class=UserProfileForm)

    def dehydrate_languages(self, bundle):
        id_user = bundle.data['id']
        up = UserProfile.objects.get(pk=id_user)

        for i in bundle.data['languages']: 
            # i = {id: id_language, name:'Spanish'}
            lang = Language.objects.get(pk=i.data['id'])
            ul = UserLanguage.objects.get(language=lang, user_profile=up)
            i.data['level'] = ul.level
            i.data.pop('id')
        return bundle.data['languages']
        

    def apply_authorization_limits(self, request, object_list=None):
        if request and request.method in ('GET'):
            if 'from' in request.GET and 'to' in request.GET:
                initial = request.GET['from']
                final = request.GET['to']
                #initial = request.META['HTTP_FROM']
                #final = request.META['HTTP_TO']
                return object_list.all()[initial:final]
            elif 'pk' in request.GET: 
                return object_list.filter(pk=request.GET['pk'])
            else: 
                return object_list.filter(user=request.user)

    @transaction.commit_on_success
    def post_detail(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format = 'application/json')
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)       
        up = UserProfile.objects.get(user=request.user)

        UserLanguage.objects.filter(user_profile_id=up.id).delete()
        if 'languages' in bundle.data:
            for lang in bundle.data['languages']:
                if lang['level'] not in LANGUAGES_LEVEL_CHOICES_KEYS: raise Exception("Incorrect level: it doesn't exist!!")
                UserLanguage.objects.get_or_create(user_profile_id=up.id, language_id=Language.objects.get(name=lang['name']).id, level=lang['level'])
            bundle.data.pop('languages')

        for i in bundle.data:
            if hasattr(up, i): setattr(up, i, bundle.data.get(i))
        up.save()
        self.method = 'POST'
        updated_bundle = self.dehydrate(bundle)
        updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
        return self.create_response(request, updated_bundle, response_class=HttpAccepted) 
    
    def post_list(self, request, **kwargs):
        print "no autorizado el post_list"
        return self.create_response(request, {}, response_class=HttpForbidden)

    def dehydrate(self, bundle):
        if self.method:
            bundle.data = {}
            bundle.data['status'] = True
            bundle.data['code'] = 204
            bundle.data['data'] = 'Updated'
            self.method = None
            return bundle   
        else:
             return super(UserProfileResource, self).dehydrate(bundle)  
    
    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):    
            try:
                #print kwargs
                #print request
                callback = getattr(self, view)
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


