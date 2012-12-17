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
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.db.models import Q

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
        result_dict = dict()     
        filters = Q(receiver=prof)|Q(sender=prof)
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
            elif key == 'search':
                list_value = value.split(' ')
                filter_search = Q()
                for k in list_value:
                     filter_search = filter_search | Q(receiver__user__first_name__icontains = k) | Q(receiver__user__last_name__icontains = k) 
                     filter_search = filter_search | Q(requests__private_message__icontains= k) | Q(invites__private_message__icontains= k) | Q(messages__private_message__icontains= k) | Q(friendship__message__icontains= k)
                     filter_search = filter_search | Q(requests__wing__name__icontains=k) | Q(invites__wing__name__icontains=k)
                     #filter_search = filter_search | Q(notifications_receiver__= k) | Q(receiver__user__last_name__icontains = k)                 
                filters = filters & filter_search                           
        try:
            my_notifications = Notifications.objects.filter(filters).order_by('-created')
            for i in my_notifications:
                print i.__dict__
                if not i.reference in result_dict:
                    aux = NotificationsList()
                    aux.id = i.pk
                    aux.created = i.created
                    if (i.receiver == prof):
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
                        inv = Invites.objects.get(pk = i.pk)     
                        additional_list = i.get_subclass().all()
                        for additional in additional_list:
                            aux.start_date = additional.start_date
                            aux.end_date = additional.end_date
                            aux.num_people = additional.num_people  
                            add_class = additional.get_class_name()                                                                        
                        aux.message = req.wing.name
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
                    aux.med_avatar =  prof_aux.medium_avatar
                    aux.age = prof_aux.get_age()
                    aux.verified = False                    
                    aux.location = prof_aux.current_city.stringify()
                    aux.name = '%s %s' % (prof_aux.user.first_name, prof_aux.user.last_name)

                    aux.connected = 'F'
                    ## Add the result                                                                     
                    result_dict[i.reference] = aux          
        except Exception, e:
            raise e
            #return self.create_response(request, {"status":False, "msg":e, "code":"403"}, response_class = HttpResponse)   
        result = []
        for key, value in result_dict.items():
            result.append(value)         
        return self.create_response(request, {"status":True, "msg":"OK", "data" : [i.jsonable() for i in result], "code":"200"}, response_class = HttpResponse)
            
        
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

class RequestsInvitesListResource(ModelResource):
    
    class Meta:
        object_class = Requests
        queryset = Requests.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True  
        resource_name = 'requestsinviteslist'                  

    def get_list(self, request, **kwargs):
        ## We are doin it the hard way
        try:
            prof = UserProfile.objects.get(user = request.user)
        except:
            return self.create_response(request, {"status":False, "msg":"Not a valid user", "code":"403"}, response_class = HttpResponse)
        result_dict = dict()        
        try:
            my_notifications = Notifications.objects.filter(Q(receiver=prof)|Q(sender=prof)).filter(Q(kind='requests')|Q(kind='invites')).order_by('-created')
            for i in my_notifications:
                if not i.reference in result_dict:
                    aux = NotificationsList()
                    aux.id = i.pk
                    aux.sender = i.sender_id
                    aux.receiver = i.receiver_id
                    aux.created = i.created
                    aux.reference = i.reference
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
                        aux.message = req.wing.name
                        aux.state = req.wing.name  
                        ## URL
                        aux.thread_url = '%s%srequestthread/%s' % (settings.BACKEND_SITE, add_class, aux.reference)
                    ## Invite specific               
                    elif aux.kind == 'invites':
                        inv = Invites.objects.get(pk = i.pk)     
                        additional_list = i.get_subclass().all()
                        for additional in additional_list:
                            aux.start_date = additional.start_date
                            aux.end_date = additional.end_date
                            aux.num_people = additional.num_people   
                            add_class = additional.get_class_name()                                    
                        aux.message = req.wing.name
                        aux.state = inv.state     
                        ## URL
                        aux.thread_url = '%s%sinvitethread/%s' % (settings.BACKEND_SITE, add_class, aux.reference)            
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
                    aux.name = '%s %s' % (prof.user.first_name, prof.user.last_name)                                                                        
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

class MessagesListResource(ModelResource):
    
    class Meta:
        object_class = Messages
        queryset = Messages.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True 
        resource_name = 'messageslist'                   

    def get_list(self, request, **kwargs):
        ## We are doin it the hard way
        try:
            prof = UserProfile.objects.get(user = request.user)
        except:
            return self.create_response(request, {"status":False, "msg":"Not a valid user", "code":"403"}, response_class = HttpResponse)
        result_dict = dict()        
        try:
            my_notifications = Notifications.objects.filter(Q(receiver=prof)|Q(sender=prof)).filter(kind='messages').order_by('-created')
            for i in my_notifications:
                if not i.reference in result_dict:
                    aux = NotificationsList()
                    aux.id = i.pk
                    aux.sender = i.sender_id
                    aux.receiver = i.receiver_id
                    aux.created = i.created
                    aux.reference = i.reference
                    aux.read = i.read
                    aux.kind = i.kind                                                    
                    ## Message specific                         
                    msg = Messages.objects.get(pk = i.pk)
                    aux.message = msg.private_message
                    ## URL
                    aux.thread_url = '%smessagethread/%s' % (settings.BACKEND_SITE, aux.reference)
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
                    aux.name = '%s %s' % (prof.user.first_name, prof.user.last_name)                                                                        
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

class FriendshipListResource(ModelResource):
    
    class Meta:
        object_class = Friendship
        queryset = Friendship.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiTokenAuthentication()
        authorization = Authorization()
        always_return_data = True 
        resource_name = 'friendshiplist'                   

    def get_list(self, request, **kwargs):
        ## We are doin it the hard way
        try:
            prof = UserProfile.objects.get(user = request.user)
        except:
            return self.create_response(request, {"status":False, "msg":"Not a valid user", "code":"403"}, response_class = HttpResponse)
        result_dict = dict()        
        try:
            my_notifications = Notifications.objects.filter(Q(receiver=prof)|Q(sender=prof)).filter(kind='friendship').order_by('-created')
            for i in my_notifications:
                if not i.reference in result_dict:
                    aux = NotificationsList()
                    aux.id = i.pk
                    aux.sender = i.sender_id
                    aux.receiver = i.receiver_id
                    aux.created = i.created
                    aux.reference = i.reference
                    aux.read = i.read
                    aux.kind = i.kind                    
                    ## Friendship specific                         
                    friend = Friendship.objects.get(pk = i.pk)
                    aux.message = friend.message
                    ## URL
                    aux.thread_url = '%sfriendthread/%s' % (settings.BACKEND_SITE, aux.reference)
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
                    aux.name = '%s %s' % (prof.user.first_name, prof.user.last_name)                                                                                                                                                  
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
