#Registration API
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from django.db import IntegrityError
from tastypie.exceptions import NotRegistered, BadRequest

from peoplewings.apps.registration.models import RegistrationProfile
from peoplewings.apps.registration.views import register    

class UserSignUpResource(ModelResource):

    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'newuser'
        excludes = ['is_active', 'is_staff', 'is_superuser']
        serializer = Serializer(formats=['json'])
        authentication = Authentication()
        authorization = Authorization()
        #models.signals.post_save.connect(create_api_key, sender=User)

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            print bundle.data          
            register(bundle.request, 'peoplewings.apps.registration.backends.custom.CustomBackend')
        except IntegrityError:
            raise BadRequest('The username already exists')
        return bundle

    
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id, is_superuser=True)

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


