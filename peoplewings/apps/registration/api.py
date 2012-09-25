#Registration API
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from django.db import IntegrityError
from tastypie.exceptions import NotRegistered, BadRequest
from django.utils import simplejson

from peoplewings.apps.registration.models import RegistrationProfile
from peoplewings.apps.registration.views import register    
from peoplewings.apps.ajax.utils import json_response

class UserSignUpResource(ModelResource):
    
    form_data = None
    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'newuser'
        #excludes = ['is_active', 'is_staff', 'is_superuser']
        serializer = Serializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        #models.signals.post_save.connect(create_api_key, sender=User)

    def obj_create(self, bundle, request=None, **kwargs):
        try:  
            request.POST = bundle.data
            self.form_data = register(request, 'peoplewings.apps.registration.backends.custom.CustomBackend')            
        except IntegrityError:
            raise BadRequest('The username already exists')
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

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.filter(is_active=True)
        resource_name = 'user'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        object_class = User
        authentication = Authentication()
        authorization = Authorization()
        include_resource_uri = False
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']


