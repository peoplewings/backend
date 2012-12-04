##API for Notifications
import json

from tastypie import fields
from tastypie.authentication import *
from tastypie.resources import ModelResource
from tastypie.authorization import *
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpApplicationError, HttpMethodNotAllowed
from tastypie.utils import trailing_slash
from tastypie.utils import dict_strip_unicode_keys

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
from django.db.models import Q

from peoplewings.apps.people.models import UserProfile

from models import Notifications, Requests, Invites, Messages, NotificationsAlarm, AdditionalInformation, AccomodationInformation

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.libs.bussines import *
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

from domain import *

class NotificationsResource(ModelResource):
    
    class Meta:
        object_class = Notifications
        queryset = Notifications.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True                    

    def get_list(self, request, **kwargs):
        ## We are doin it the hard way
        try:
            prof = UserProfile.objects.get(user = request.user)
        except:
            return self.create_response(request, {"status":False, "msg":"Not a valid user", "code":"403"}, response_class = HttpResponse)
        result_dict = dict()        
        try:
            my_notifications = Notifications.objects.filter(Q(receiver=prof)|Q(sender=prof)).order_by('-created')
            for i in my_notifications:
                if not i.reference in result_dict:
                    aux = NotificationsList()
                    aux.sender = i.sender_id
                    aux.receiver = i.receiver_id
                    aux.created = i.created
                    aux.reference = i.reference
                    aux.read = i.read
                    aux.kind = i.kind
                    ## Request specific
                    if aux.kind == 'requests':
                        req = Requests.objects.get(pk = i.pk)
                        additional_list = AccomodationInformation.objects.filter(notification = i)
                        for additional in additional_list:
                            aux.start_date = additional.start_date
                            aux.end_date = additional.end_date
                            aux.num_people = additional.num_people                                      
                        aux.title = req.title
                        aux.state = req.state  
                        aux.private_message = req.private_message   
                    ## Invite specific               
                    elif aux.kind == 'invites':
                        inv = Invites.objects.get(pk = i.pk)     
                        additional_list = AccomodationInformation.objects.filter(notification = i)
                        for additional in additional_list:
                            aux.start_date = additional.start_date
                            aux.end_date = additional.end_date
                            aux.num_people = additional.num_people                                      
                        aux.title = req.title
                        aux.state = req.state         
                        aux.private_message = inv.private_message    
                    ## Message specific                         
                    elif aux.kind == 'messages':
                        msg = Messages.objects.get(pk = i.pk)
                        aux.private_message = msg.message
                    #Profile specific
                    if (aux.sender == prof.pk):
                        ## YOU are the sender. Need receiver info
                        prof_aux = UserProfile.objects.get(pk = aux.receiver)                   
                    else:
                        ## YOU are the receiver. Need the sender info  
                        prof_aux = UserProfile.objects.get(pk = aux.sender)               
                    aux.med_avatar =  prof_aux.medium_avatar
                    aux.age = prof_aux.get_age()
                    aux.verified = False                    
                    aux.location = prof_aux.current_city.stringify()                                                                           
                    result_dict[aux.reference] = aux          
        except Exception, e:
            raise e
            #return self.create_response(request, {"status":False, "msg":e, "code":"403"}, response_class = HttpResponse)   
        result = []
        for key, value in result_dict.items():
            result.append(value)         
        return self.create_response(request, {"status":True, "msg":"OK", "data" : [i.jsonable() for i in result], "code":"200"}, response_class = HttpResponse)
            
        
    def get_detail(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Forbidden", "code":"403"}, response_class = HttpResponse)
    
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
