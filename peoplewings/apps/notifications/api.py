##API for Notifications
import json
from operator import itemgetter, attrgetter

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
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage

from peoplewings.apps.people.models import UserProfile

from models import Notifications, Requests, Invites, Messages, NotificationsAlarm, AdditionalInformation, AccomodationInformation, Friendship

from peoplewings.apps.ajax.utils import json_response
from peoplewings.apps.ajax.utils import CamelCaseJSONSerializer
from peoplewings.libs.customauth.models import ApiToken
from peoplewings.libs.bussines import *
from peoplewings.apps.registration.authentication import ApiTokenAuthentication

from domain import *

class NotificationsListResource(ModelResource):
    
    class Meta:
        object_class = Notifications
        queryset = Notifications.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True     
        resource_name = 'notificationslist'               

    def get_list(self, request, **kwargs):
        ## We are doin it the hard way
        try:
            prof = UserProfile.objects.get(user = request.user)
        except:
            return self.create_response(request, {"status":False, "msg":"Not a valid user", "code":"403"}, response_class = HttpResponse)

        result_dict = []     
        filters = Q(receiver=prof)|Q(sender=prof)
        order_by = '-created'

        for key, value in request.GET.items():
            if key == 'kind':
                if value == 'reqinv':
                    filters = filters & Q(kind='requests')|Q(kind='invites')
                elif value == 'msg':
                      filters = filters & Q(kind='messages')
                elif value == 'friendship':
                      filters = filters & Q(kind='friends')
            elif key == 'target':
                if value == 'received':
                    filters = filters & ~Q(first_sender = prof)
                elif value == 'sent':
                    filters = filters & Q(first_sender = prof)
            elif key == 'state' and 'kind' in [k for k, v in request.GET.items()]:
                #Filtro por estado de la request
                filters = filters & Q(requests__state = value)
        try:
            my_notifications = Notifications.objects.filter(filters).order_by('-created')
            for i in my_notifications:
                #if not i.reference in result_dict:
                aux = NotificationsList()
                aux.id = i.pk
                aux.created = i.created
                if (i.sender == prof):
                    aux.read = True
                else:
                    aux.read = i.read
                aux.kind = i.kind
                ## Request specific
                if aux.kind == 'requests':
                    req = Requests.objects.get(pk = i.pk)
                    additional_list = i.get_subclass().all()        
                    for additional in additional_list:
                        aux.start_date = additional.start_date
                        aux.end_date = additional.end_date
                        aux.num_people = additional.num_people 
                        add_class = additional.get_class_name() 
                        aux.wing_type = add_class                             
                    aux.message = req.wing.name
                    aux.state = req.state
                    if i.first_sender == prof:                           
                        aux.flag_direction = True
                    else:
                        aux.flag_direction =   False                      
                    ## URL                        
                    aux.thread_url = '%s%srequestthread/%s' % (settings.BACKEND_SITE, add_class, i.reference)
                    ## Invite specific               
                elif aux.kind == 'invites':
                    print i.id                  
                    inv = Invites.objects.get(pk = i.pk) 
                    print inv
                    additional_list = i.get_subclass().all()
                    for additional in additional_list:
                        aux.start_date = additional.start_date
                        aux.end_date = additional.end_date
                        aux.num_people = additional.num_people  
                        add_class = additional.get_class_name()   
                        aux.wing_type = add_class                                                                            
                    aux.message = inv.wing.name
                    aux.state = inv.state   
                    if i.first_sender == prof.pk:
                         aux.flag_direction = True
                    else:
                        aux.flag_direction =   False          
                    ## URL
                    aux.thread_url = '%s%sinvitethread/%s' % (settings.BACKEND_SITE, add_class, i.reference)
                ## Message specific                         
                elif aux.kind == 'messages':
                    msg = Messages.objects.get(pk = i.pk)
                    aux.content = msg.private_message
                    ## URL
                    aux.thread_url = '%smessagethread/%s' % (settings.BACKEND_SITE, i.reference)
                ## Friendship specific                         
                elif aux.kind == 'friendship':
                    friend = Friendship.objects.get(pk = i.pk)
                    aux.content = friend.message
                    ## URL
                    aux.thread_url = '%sfriendthread/%s' % (settings.BACKEND_SITE, i.reference)
                #Profile specific
                if (i.sender == prof):
                    ## YOU are the sender. Need receiver info
                    prof_aux = UserProfile.objects.get(pk = i.receiver.pk)                   
                else:
                    ## YOU are the receiver. Need the sender info  
                    prof_aux = UserProfile.objects.get(pk = i.sender.pk)     
                aux.interlocutor_id = prof_aux.pk          
                aux.avatar =  prof_aux.thumb_avatar
                aux.age = prof_aux.get_age()
                aux.verified = False                    
                aux.location = prof_aux.current_city.stringify()
                aux.name = '%s %s' % (prof_aux.user.first_name, prof_aux.user.last_name)

                aux.connected = 'F'
                ## Add the result                                                                     
                result_dict.append(aux)                
        except Exception, e:
            raise e
            #return self.create_response(request, {"status":False, "msg":e, "code":"403"}, response_class = HttpResponse)   
        result = []
        #Here we will apply search filter and order_by
        for key, value in request.GET.items():
            if key == 'search':
                list_value = value.split(' ')
                search_list = []
                for k in list_value:
                    aux_dict_small = [o.thread_url for o in result_dict if o.search(k)]
                    aux_dict_extended = [o for o in result_dict if o.thread_url in aux_dict_small]
                    search_list += aux_dict_extended
                result_dict = search_list
            elif key == 'order':
                if  value == 'date':
                    result_dict = sorted(result_dict, key=attrgetter('created'), reverse=True)
                elif value == 'interlocutor':                                        
                    result_dict = sorted(result_dict, key=attrgetter('name'), reverse=False)
                elif value == 'read':
                    result_dict = sorted(result_dict, key=attrgetter('read'), reverse=False)
                elif value == 'date-start' and 'reqinv' in [val for key, val in request.GET.items() if key == 'kind']:
                    result_dict = sorted(result_dict, key=attrgetter('start_date'), reverse=True)
                elif value == 'type' and 'reqinv' in [val for key, val in request.GET.items() if key == 'kind']:
                    result_dict = sorted(result_dict, key=attrgetter('wing_type'), reverse=True)
        for o in result_dict:
            if o.thread_url not in [r.thread_url for r in result]:
                result.append(o)
        num_page = int(request.GET.get('page', 1))
        paginator = Paginator(result, 1)
        try:
            page = paginator.page(num_page)
        except InvalidPage:
            return self.create_response(request, {"msg":"Sorry, no results on that page.", "code":413, "status":False}, response_class=HttpForbidden)
        return self.create_response(request, {"status":True, "msg":"OK", "data" : [i.jsonable() for i in page.object_list], "code":"200"}, response_class = HttpResponse)

        
    def get_detail(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Method not allowed", "code":"403"}, response_class = HttpResponse)
    
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


class AccomodationRequestThreadResource(ModelResource):
    
    class Meta:
        object_class = Requests
        queryset = Requests.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True 
        resource_name = 'accomodationrequestthread'                    

    def get_detail(self, request, **kwargs):
        ## We are doin it the hard way
        ref = kwargs['pk']
        result = []
        try:
            thread = Notifications.objects.filter(reference=ref).order_by('created')
        except:
            return self.create_response(request, {"status":False, "data":"Could not find any thread with that reference id", "code":"403"}, response_class = HttpResponse)
        for i in thread:
            aux = AccomodationRequestThread()
            ## Notif specific
            aux.id  = i.pk
            aux.sender = i.sender
            aux.receiver = i.receiver
            aux.created = i.created
            aux.reference = i.reference
            aux.read = i.read
            aux.kind = i.kind
            ## AccomodationRequest specific
            try:
                req = Requests.objects.get(pk = aux.id)
                additional_list = AccomodationInformation.objects.filter(notification = i)
            except:
               return self.create_response(request, {"status":False, "msg":"Could not load the request", "code":"403"}, response_class = HttpResponse) 
            aux.wing_name = req.wing.name
            aux.wing_id = req.wing.pk
            aux.state = req.state              
            for additional in additional_list: 
                aux.start_date = additional.start_date
                aux.end_date = additional.end_date
                aux.num_people = additional.num_people
                aux.transport = additional.transport
            aux.private_message = req.private_message
            #Sender specific
            aux.nameS = '%s %s' % (i.sender.user.first_name, i.sender.user.last_name)
            aux.ageS = i.sender.age
            aux.verifiedS = False
            aux.locationS = i.sender.current_city.stringify()
            aux.friendsS = len(i.sender.relationships.filter())
            aux.referencesS = len(i.sender.references.filter())
            aux.med_avatarS =  i.sender.medium_avatar
            aux.small_avatarS = i.sender.thumb_avatar
            #Receiver specific
            aux.nameR = '%s %s' % (i.receiver.user.first_name, i.receiver.user.last_name)
            aux.ageR = i.receiver.age
            aux.verifiedR = False
            aux.locationR = i.receiver.current_city.stringify()
            aux.friendsR = len(i.receiver.relationships.filter())
            aux.referencesR = len(i.receiver.references.filter())
            aux.med_avatarR =  i.receiver.medium_avatar
            aux.small_avatarR = i.receiver.thumb_avatar
            result.append(aux)
        return self.create_response(request, {"status":True, "msg":"OK", "data" : [i.jsonable() for i in result], "code":"200"}, response_class = HttpResponse)
            
        
    def get_list(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Method not allowed", "code":"403"}, response_class = HttpResponse)
    
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

class InviteRequestThreadResource(ModelResource):
    
    class Meta:
        object_class = Requests
        queryset = Requests.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True 
        resource_name = 'inviterequestthread'                    

    def get_detail(self, request, **kwargs):
        ## We are doin it the hard way
        ref = kwargs['pk']
        result = []
        try:
            thread = Notifications.objects.filter(reference=ref).order_by('created')
        except:
            return self.create_response(request, {"status":False, "data":"Could not find any thread with that reference id", "code":"403"}, response_class = HttpResponse)
        for i in thread:
            aux = AccomodationRequestThread()
            ## Notif specific
            aux.id  = i.pk
            aux.sender = i.sender
            aux.receiver = i.receiver
            aux.created = i.created
            aux.reference = i.reference
            aux.read = i.read
            aux.kind = i.kind
            ## AccomodationRequest specific
            try:
                req = Requests.objects.get(pk = aux.id)
                additional_list = AccomodationInformation.objects.filter(notification = i)
            except:
               return self.create_response(request, {"status":False, "msg":"Could not load the request", "code":"403"}, response_class = HttpResponse) 
            aux.wing_name = req.wing.name
            aux.wing_id = req.wing.pk
            aux.state = req.state              
            for additional in additional_list: 
                aux.start_date = additional.start_date
                aux.end_date = additional.end_date
                aux.num_people = additional.num_people
                aux.transport = additional.transport
            aux.private_message = req.private_message
            #Sender specific
            aux.nameS = '%s %s' % (i.sender.user.first_name, i.sender.user.last_name)
            aux.ageS = i.sender.age
            aux.verifiedS = False
            aux.locationS = i.sender.current_city.stringify()
            aux.friendsS = len(i.sender.relationships.filter())
            aux.referencesS = len(i.sender.references.filter())
            aux.med_avatarS =  i.sender.medium_avatar
            aux.small_avatarS = i.sender.thumb_avatar
            #Receiver specific
            aux.nameR = '%s %s' % (i.receiver.user.first_name, i.receiver.user.last_name)
            aux.ageR = i.receiver.age
            aux.verifiedR = False
            aux.locationR = i.receiver.current_city.stringify()
            aux.friendsR = len(i.receiver.relationships.filter())
            aux.referencesR = len(i.receiver.references.filter())
            aux.med_avatarR =  i.receiver.medium_avatar
            aux.small_avatarR = i.receiver.thumb_avatar
            result.append(aux)
        return self.create_response(request, {"status":True, "msg":"OK", "data" : [i.jsonable() for i in result], "code":"200"}, response_class = HttpResponse)
            
        
    def get_list(self, request, **kwargs):
        ##DO NOTHING
        return self.create_response(request, {"status":False, "data":"Method not allowed", "code":"403"}, response_class = HttpResponse)
    
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
